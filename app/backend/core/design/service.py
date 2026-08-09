# pyre-ignore-all-errors
"""Unified structural design service — dispatches design to the correct module.

Covers all 12 member types per instructions.md §14 and provides
a design loop for iterative convergence per instructions.md §16.
"""

from typing import Any, Dict, List

from ...models.member import MemberType      # type: ignore
from .beam import BeamDesign                 # type: ignore
from .column import ColumnDesign             # type: ignore
from .slab_oneway import OneWaySlabDesign    # type: ignore
from .slab_twoway import TwoWaySlabDesign    # type: ignore
from .slab_beamless import FlatPlateDesign   # type: ignore
from .shear_wall import ShearWallDesign      # type: ignore
from .retaining_wall import RetainingWallDesign, RetainingWallInput # type: ignore
from .footing_isolated import IsolatedFootingDesign                 # type: ignore
from .footing_combined import CombinedFootingDesign                 # type: ignore
from .footing_raft import RaftFoundationDesign                      # type: ignore
from .staircase import StaircaseDesign       # type: ignore
from .dome import DomeDesign                 # type: ignore
from .pile import PileDesign                 # type: ignore
from .cfs import CFSDesign                   # type: ignore
from .detailing import DetailingEngine       # type: ignore


class StructuralDesignService:
    """Unified service for structural member design dispatch."""

    @staticmethod
    def design_member(
        member_type: MemberType, inputs: Dict[str, Any], forces: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Dispatches design to the appropriate module based on member type."""

        fc = float(inputs.get("fc", 25.0) or 25.0)
        fy = float(inputs.get("fy", 500.0) or 500.0)
        width = float(inputs.get("width", 300.0) or 300.0)
        depth = float(inputs.get("depth", 600.0) or 600.0)
        cover = float(inputs.get("cover", 40.0) or 40.0)
        # Note: We keep these local for logic below, but we'll pass them to schemas which handle defaults.

        # ── BEAM ─────────────────────────────────────────────
        if member_type == MemberType.BEAM:
            from backend.api.schemas.design_standards import BeamDesignInput, BeamDesignForces, MaterialProps
            beam_input = BeamDesignInput(
                width=width, depth=depth, cover=inputs.get("cover", 60.0), # pyre-ignore[6]
                material=MaterialProps(
                    fc=fc if fc else 25.0, 
                    fy=fy if fy else 500.0, 
                    fy_v=inputs.get("fy_v", fy if fy else 500.0)
                )
            )
            beam_forces = BeamDesignForces(
                Mu=forces.get("Mu", 0.0), Vu=forces.get("Vu", 0.0)
            )
            flexure = BeamDesign.design_flexure(beam_input, beam_forces)
            shear = BeamDesign.design_shear(beam_input, beam_forces)
            
            # Detailing extraction
            As_req = flexure.As_req_mm2
            Av_over_s = shear.Av_over_s_req
            effective_d = (depth if depth else 600.0) - (inputs.get("cover", 60.0))
            
            detailing = {
                "flexural_schedule": DetailingEngine.select_flexural_bars(As_req, width if width else 300.0),
                "shear_schedule": DetailingEngine.select_shear_spacing(Av_over_s, effective_d)
            }
            
            return {"flexure": flexure.model_dump(), "shear": shear.model_dump(), "detailing": detailing}

        # ── COLUMN ───────────────────────────────────────────
        elif member_type == MemberType.COLUMN:
            from backend.api.schemas.design_standards import ColumnDesignInput, ColumnDesignForces, MaterialProps, RebarLayer
            rebar_layers_raw = inputs.get(
                "rebar_layers",
                [{"depth": 50, "As": 800}, {"depth": (depth if depth else 600.0) - 50, "As": 800}],
            )
            rebar_layers = [RebarLayer(**r) for r in rebar_layers_raw]
            
            col_input = ColumnDesignInput(
                width=width, depth=depth, # pyre-ignore[6]
                material=MaterialProps(
                    fc=fc if fc else 28.0, 
                    fy=fy if fy else 420.0, 
                    fy_v=inputs.get("fy_v", fy if fy else 420.0)
                ),
                rebar_layers=rebar_layers,
                is_sway=inputs.get("is_sway", True),
                klu_over_r=inputs.get("klu_over_r", 10.0)
            )
            col_forces = ColumnDesignForces(
                Pu=forces.get("Pu", 0.0), Mux=forces.get("Mux", forces.get("Mu", 0.0)),
                Muy=forces.get("Muy", 0.0), Vu=forces.get("Vu", 0.0)
            )
            
            diag = ColumnDesign.generate_interaction_diagram(col_input, col_forces)
            shear = ColumnDesign.design_shear(col_input, col_forces)
            # Biaxial check
            biaxial = ColumnDesign.check_biaxial_capacity(col_input, col_forces, diag.points, diag.points)
            
            As_req = sum(r.As for r in rebar_layers)
            detailing = DetailingEngine.detail_column(
                width if width else 400.0, 
                depth if depth else 400.0, 
                As_req, 
                pu_kn=col_forces.Pu, 
                fc=fc if fc else 28.0
            )
            
            return {
                "interaction_diagram": {"points": [p.model_dump() for p in diag.points]},
                "shear": shear.model_dump(),
                "biaxial_check": biaxial.model_dump(),
                "detailing": detailing
            }

        # ── SLAB (ONE‑WAY) ───────────────────────────────────
        elif member_type == MemberType.SLAB_ONEWAY:
            from backend.api.schemas.design_standards import SlabDesignInput, OneWaySlabForces, MaterialProps
            slab_input = SlabDesignInput(
                thickness=depth, cover=inputs.get("cover", 20.0), bar_dia=inputs.get("bar_dia", 10.0), # pyre-ignore[6]
                material=MaterialProps(
                    fc=fc if fc else 25.0, 
                    fy=fy if fy else 500.0, 
                    fy_v=inputs.get("fy_v", fy if fy else 500.0)
                )
            )
            slab_forces = OneWaySlabForces(Mu=forces.get("Mu", 0.0))
            slab_res = OneWaySlabDesign.design_flexure(slab_input, slab_forces)
            
            As_main = slab_res.As_flexure_mm2_m
            As_temp = slab_res.As_temp_mm2_m
            detailing = DetailingEngine.detail_slab(depth if depth else 150.0, As_main, As_temp)
            
            return {"slab_oneway": slab_res.model_dump(), "detailing": detailing}

        # ── SLAB (TWO‑WAY) ───────────────────────────────────
        elif member_type == MemberType.SLAB_TWOWAY:
            from backend.api.schemas.design_standards import SlabDesignInput, TwoWaySlabForces, MaterialProps
            slab_input = SlabDesignInput(
                thickness=depth, cover=inputs.get("cover", 20.0), bar_dia=inputs.get("bar_dia", 10.0), # pyre-ignore[6]
                material=MaterialProps(
                    fc=fc if fc else 25.0, 
                    fy=fy if fy else 500.0, 
                    fy_v=inputs.get("fy_v", fy if fy else 500.0)
                )
            )
            slab_forces = TwoWaySlabForces(
                Mu_x=forces.get("Mu_x", forces.get("Mu", 0.0)),
                Mu_y=forces.get("Mu_y", 0.0)
            )
            slab_res = TwoWaySlabDesign.design_flexure_fea(slab_input, slab_forces)
            return {"slab_twoway": slab_res.model_dump()}

        # ── SLAB (BEAMLESS / FLAT PLATE) ─────────────────────
        elif member_type == MemberType.SLAB_BEAMLESS:
            from backend.api.schemas.design_standards import PunchingShearInput
            d_slab = (depth if depth else 200.0) - (inputs.get("cover", 30.0))
            punch_in = PunchingShearInput(
                Vu=forces.get("Vu", 0.0),
                Mu_unbalanced=forces.get("Mu_unbalanced", 0.0),
                c1=inputs.get("column_c1", 400.0),
                c2=inputs.get("column_c2", 400.0),
                location=inputs.get("column_location", "interior")
            )
            punch = FlatPlateDesign.check_punching_shear(punch_in, d_slab, fc if fc else 25.0)
            return {"punching_shear": punch.model_dump()}

        # ── SHEAR WALL ───────────────────────────────────────
        elif member_type == MemberType.SHEAR_WALL:
            from backend.api.schemas.design_standards import ShearWallInput, ShearWallForces, SlenderWallInput, MaterialProps
            lw = width # logical mapping
            tw = inputs.get("thickness", 200.0)
            hw = inputs.get("height", 3500.0)
            
            shear_input = ShearWallInput(
                lw=lw, hw=hw, tw=tw, # pyre-ignore[6]
                material=MaterialProps(
                    fc=fc if fc else 25.0, 
                    fy=fy if fy else 500.0, 
                    fy_v=inputs.get("fy_v", fy if fy else 500.0)
                )
            )
            shear_forces = ShearWallForces(
                Vu=forces.get("Vu", 0.0), Pu=forces.get("Pu", 0.0), Mu=forces.get("Mu", 0.0)
            )
            shear_res = ShearWallDesign.design_shear(shear_input, shear_forces)
            
            slender_input = SlenderWallInput(
                lw=lw, hw=hw, tw=tw, # pyre-ignore[6]
                As=inputs.get("As", 0.0025 * tw * 1000),
                material=MaterialProps(
                    fc=fc if fc else 25.0, 
                    fy=fy if fy else 500.0, 
                    fy_v=inputs.get("fy_v", fy if fy else 500.0)
                )
            )
            slender_res = ShearWallDesign.design_slender_wall(
                slender_input, Mu=forces.get("Mu", 0.0), Pu=forces.get("Pu", 0.0)
            )
            return {"shear_check": shear_res.model_dump(), "slender_wall_check": slender_res.model_dump()}

        # ── RETAINING WALL ───────────────────────────────────
        elif member_type == MemberType.RETAINING_WALL:
            from backend.api.schemas.design_standards import RetainingWallInput
            rw_input = RetainingWallInput(
                height_m=float(inputs.get("height", 3.0) or 3.0), # pyre-ignore[6]
                soil_gamma=inputs.get("soil_gamma", 18.0),
                soil_phi=inputs.get("soil_phi", 30.0),
                surcharge_kpa=inputs.get("surcharge", 10.0),
                water_table_depth_m=inputs.get("water_table_depth"),
            )
            pressures = RetainingWallDesign.calculate_lateral_pressures(rw_input)
            return {"lateral_pressures": pressures.model_dump()["pressures"], "status": "OK"}

        # ── ISOLATED FOOTING ─────────────────────────────────
        elif member_type == MemberType.FOOTING_ISOLATED:
            from backend.api.schemas.design_standards import IsolatedFootingInput, IsolatedFootingForces, MaterialProps
            footing_input = IsolatedFootingInput(
                q_allow=float(inputs.get("q_allow", 150.0) or 150.0), # pyre-ignore[6]
                cover=inputs.get("cover", 75.0),
                material=MaterialProps(
                    fc=fc if fc else 28.0, 
                    fy=fy if fy else 420.0, 
                    fy_v=inputs.get("fy_v", fy if fy else 420.0)
                )
            )
            footing_forces = IsolatedFootingForces(
                P=forces.get("P", forces.get("Pu", 0.0)),
                Mx=forces.get("Mx", forces.get("Mu", 0.0)),
                My=forces.get("My", 0.0)
            )
            res = IsolatedFootingDesign.design(footing_input, footing_forces)
            
            thickness = getattr(res, "t_mm", 400.0)
            As_req = getattr(res, "As_req_mm2", 0)
            detailing = DetailingEngine.detail_slab(thickness, As_req, As_req, main_dia=16, temp_dia=16)
            
            return {"footing": res.model_dump(), "detailing": detailing}

        # ── COMBINED FOOTING ─────────────────────────────────
        elif member_type == MemberType.FOOTING_COMBINED:
            from backend.api.schemas.design_standards import CombinedFootingInput, CombinedFootingForces, MaterialProps
            comb_input = CombinedFootingInput(
                c_c_dist=float(inputs.get("c_c_dist", 5.0) or 5.0), # pyre-ignore[6]
                q_allow=float(inputs.get("q_allow", 150.0) or 150.0), # pyre-ignore[6]
                material=MaterialProps(
                    fc=fc if fc else 28.0, 
                    fy=fy if fy else 420.0, 
                    fy_v=inputs.get("fy_v", fy if fy else 420.0)
                )
            )
            comb_forces = CombinedFootingForces(
                P1=forces.get("P1", 500.0),
                P2=forces.get("P2", 700.0)
            )
            res = CombinedFootingDesign.design(comb_input, comb_forces)
            return {"combined_footing": res.model_dump()}

        # ── RAFT FOUNDATION ──────────────────────────────────
        elif member_type == MemberType.FOOTING_RAFT:
            from backend.api.schemas.design_standards import RaftFoundationInput, RaftFoundationForces, MaterialProps
            raft_input = RaftFoundationInput(
                thickness=depth, # pyre-ignore[6]
                cover=inputs.get("cover", 75.0),
                material=MaterialProps(
                    fc=fc if fc else 25.0, 
                    fy=fy if fy else 500.0, 
                    fy_v=inputs.get("fy_v", fy if fy else 500.0)
                )
            )
            raft_forces = RaftFoundationForces(
                Mu_x=forces.get("Mu_x", forces.get("Mu", 0.0)),
                Mu_y=forces.get("Mu_y", 0.0)
            )
            res = RaftFoundationDesign.design_flexure_fea(raft_input, raft_forces)
            return {"raft_flexure": res.model_dump()}

        # ── STAIRCASE ────────────────────────────────────────
        elif member_type == MemberType.STAIRCASE:
            from backend.api.schemas.design_standards import StaircaseInput, StaircaseForces, MaterialProps
            staircase_input = StaircaseInput(
                going=float(inputs.get("going", 3.0) or 3.0), # pyre-ignore[6]
                rise=inputs.get("rise", 150.0),
                tread=inputs.get("tread", 300.0),
                width=width, # pyre-ignore[6]
                material=MaterialProps(
                    fc=fc if fc else 25.0, 
                    fy=fy if fy else 500.0, 
                    fy_v=inputs.get("fy_v", fy if fy else 500.0)
                )
            )
            staircase_forces = StaircaseForces(
                LL=forces.get("LL", inputs.get("LL", 3.0))
            )
            res = StaircaseDesign.design(staircase_input, staircase_forces)
            return {"staircase": res.model_dump()}

        # ── DOME ─────────────────────────────────────────────
        elif member_type == MemberType.DOME:
            from backend.api.schemas.design_standards import DomeInput, DomeForces
            dome_input = DomeInput(
                radius=float(inputs.get("radius", 10.0) or 10.0), # pyre-ignore[6]
                thickness=inputs.get("thickness", 0.15),
                theta_edge_deg=inputs.get("theta_edge", 45.0)
            )
            dome_forces = DomeForces(
                DL=inputs.get("DL", 3.0),
                LL=forces.get("LL", inputs.get("LL", 0.5))
            )
            res = DomeDesign.calculate_membrane_forces(dome_input, dome_forces)
            return {"dome": res.model_dump()}

        return {"status": "Unknown member type or design logic pending"}

    @staticmethod
    def design_loop(
        members: List[Dict[str, Any]],
        max_iter: int = 10,
        tol: float = 0.01,
    ) -> Dict[str, Any]:
        """Iterative design loop per instructions.md §16.

        Each member dict must contain:
          - "member_type": MemberType
          - "inputs": dict with geometry/material
          - "forces": dict with Mu, Vu, Pu, etc.

        Returns converged design results and iteration count.
        """
        results = {}
        converged = False

        for iteration in range(1, max_iter + 1):
            max_change = 0.0

            for i, member in enumerate(members):
                mtype = member["member_type"]
                inputs = member["inputs"]
                forces = member["forces"]

                result = StructuralDesignService.design_member(mtype, inputs, forces)
                member_key = member.get("label", f"M-{i+1}")

                # Check if any sub-result failed
                any_fail = False
                for k, v in result.items():
                    if isinstance(v, dict):
                        st = v.get("status", "")
                        if "FAIL" in str(st).upper() or "Inadequate" in str(st):
                            any_fail = True

                # Auto-resize on failure (increase depth by 10%)
                if any_fail and iteration < max_iter:
                    old_depth = inputs.get("depth", inputs.get("thickness", 600.0))
                    new_depth = old_depth * 1.10
                    if "thickness" in inputs:
                        member["inputs"]["thickness"] = new_depth
                    else:
                        member["inputs"]["depth"] = new_depth
                    max_change = max(max_change, abs(new_depth - old_depth) / old_depth)

                results[member_key] = {
                    "iteration": iteration,
                    "design": result,
                    "converged_size": not any_fail,
                }

            if max_change < tol:
                converged = True
                break

        return {
            "converged": converged,
            "iterations": iteration,
            "member_results": results,
        }
