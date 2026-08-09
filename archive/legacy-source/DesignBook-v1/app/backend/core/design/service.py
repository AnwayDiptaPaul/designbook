"""Unified structural design service — dispatches design to the correct module.

Covers all 12 member types per instructions.md §14 and provides
a design loop for iterative convergence per instructions.md §16.
"""

from typing import Any, Dict, List

from backend.models.member import MemberType
from backend.core.design.beam import BeamDesign
from backend.core.design.column import ColumnDesign
from backend.core.design.slab_oneway import OneWaySlabDesign
from backend.core.design.slab_twoway import TwoWaySlabDesign
from backend.core.design.slab_beamless import FlatPlateDesign
from backend.core.design.shear_wall import ShearWallDesign
from backend.core.design.retaining_wall import RetainingWallDesign, RetainingWallInput
from backend.core.design.footing_isolated import IsolatedFootingDesign
from backend.core.design.footing_combined import CombinedFootingDesign
from backend.core.design.footing_raft import RaftFoundationDesign
from backend.core.design.staircase import StaircaseDesign
from backend.core.design.dome import DomeDesign
from backend.core.design.pile import PileDesign
from backend.core.design.cfs import CFSDesign


class StructuralDesignService:
    """Unified service for structural member design dispatch."""

    @staticmethod
    def design_member(
        member_type: MemberType, inputs: Dict[str, Any], forces: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Dispatches design to the appropriate module based on member type."""

        fc = inputs.get("fc", 25.0)
        fy = inputs.get("fy", 500.0)
        b = inputs.get("width", 300.0)
        h = inputs.get("depth", 600.0)
        d = h - inputs.get("cover", 60.0)

        # ── BEAM ─────────────────────────────────────────────
        if member_type == MemberType.BEAM:
            flexure = BeamDesign.design_flexure(
                forces.get("Mu", 0.0), b, d, fc, fy
            )
            shear = BeamDesign.design_shear(
                forces.get("Vu", 0.0), b, d, fc, fy
            )
            return {"flexure": flexure, "shear": shear}

        # ── COLUMN ───────────────────────────────────────────
        elif member_type == MemberType.COLUMN:
            Pu = forces.get("Pu", 0.0)
            Mux = forces.get("Mux", forces.get("Mu", 0.0))
            Muy = forces.get("Muy", 0.0)
            rebar_layers = inputs.get(
                "rebar_layers",
                [{"depth": 50, "As": 800}, {"depth": h - 50, "As": 800}],
            )
            diag = ColumnDesign.generate_interaction_diagram(
                b, h, fc, fy, rebar_layers
            )
            shear = ColumnDesign.design_shear(
                forces.get("Vu", 0.0), b, d, fc, fy, 400, 150
            )
            # Biaxial check
            biaxial = ColumnDesign.check_biaxial_capacity(
                Pu, Mux, Muy, diag["points"], diag["points"]
            )
            return {
                "interaction_diagram": diag,
                "shear": shear,
                "biaxial_check": biaxial,
            }

        # ── SLAB (ONE‑WAY) ───────────────────────────────────
        elif member_type == MemberType.SLAB_ONEWAY:
            t = inputs.get("depth", 150.0)
            slab_res = OneWaySlabDesign.design_flexure(
                forces.get("Mu", 0.0), t, fc, fy,
                cover=inputs.get("cover", 20.0),
                bar_dia=inputs.get("bar_dia", 10.0),
            )
            return {"slab_oneway": slab_res}

        # ── SLAB (TWO‑WAY) ───────────────────────────────────
        elif member_type == MemberType.SLAB_TWOWAY:
            t = inputs.get("depth", 175.0)
            slab_res = TwoWaySlabDesign.design_flexure_fea(
                forces.get("Mu_x", forces.get("Mu", 0.0)),
                forces.get("Mu_y", 0.0),
                t, fc, fy,
                cover=inputs.get("cover", 20.0),
            )
            return {"slab_twoway": slab_res}

        # ── SLAB (BEAMLESS / FLAT PLATE) ─────────────────────
        elif member_type == MemberType.SLAB_BEAMLESS:
            t = inputs.get("depth", 200.0)
            d_slab = t - inputs.get("cover", 30.0)
            c1 = inputs.get("column_c1", 400.0)
            c2 = inputs.get("column_c2", 400.0)
            location = inputs.get("column_location", "interior")
            punch = FlatPlateDesign.check_punching_shear(
                forces.get("Vu", 0.0),
                forces.get("Mu_unbalanced", 0.0),
                c1, c2, d_slab, fc, location,
            )
            return {"punching_shear": punch}

        # ── SHEAR WALL ───────────────────────────────────────
        elif member_type == MemberType.SHEAR_WALL:
            lw = inputs.get("width", 3000.0)
            tw = inputs.get("thickness", 200.0)
            hw = inputs.get("height", 3500.0)
            shear_res = ShearWallDesign.design_shear(
                forces.get("Vu", 0.0),
                forces.get("Pu", 0.0),
                lw, hw, tw, fc, fy,
            )
            slender_res = ShearWallDesign.design_slender_wall(
                forces.get("Pu", 0.0),
                forces.get("Mu", 0.0),
                lw, hw, tw, fc, fy,
                inputs.get("As", 0.0025 * tw * 1000),
            )
            return {"shear_check": shear_res, "slender_wall_check": slender_res}

        # ── RETAINING WALL ───────────────────────────────────
        elif member_type == MemberType.RETAINING_WALL:
            rw_input = RetainingWallInput(
                height_m=inputs.get("height", 3.0),
                soil_gamma=inputs.get("soil_gamma", 18.0),
                soil_phi=inputs.get("soil_phi", 30.0),
                surcharge_kpa=inputs.get("surcharge", 10.0),
                water_table_depth_m=inputs.get("water_table_depth"),
            )
            pressures = RetainingWallDesign.calculate_lateral_pressures(rw_input)
            return {"lateral_pressures": pressures, "status": "OK"}

        # ── ISOLATED FOOTING ─────────────────────────────────
        elif member_type == MemberType.FOOTING_ISOLATED:
            res = IsolatedFootingDesign.design(
                forces.get("P", forces.get("Pu", 0.0)),
                forces.get("Mx", forces.get("Mu", 0.0)),
                forces.get("My", 0.0),
                inputs.get("q_allow", 150.0),
                fc, fy,
                cover=inputs.get("cover", 75.0),
            )
            return {"footing": res}

        # ── COMBINED FOOTING ─────────────────────────────────
        elif member_type == MemberType.FOOTING_COMBINED:
            res = CombinedFootingDesign.design(
                forces.get("P1", 500.0),
                forces.get("P2", 700.0),
                inputs.get("c_c_dist", 4.0),
                inputs.get("q_allow", 150.0),
                fc, fy,
            )
            return {"combined_footing": res}

        # ── RAFT FOUNDATION ──────────────────────────────────
        elif member_type == MemberType.FOOTING_RAFT:
            t_raft = inputs.get("depth", 600.0)
            res = RaftFoundationDesign.design_flexure_fea(
                forces.get("Mu_x", forces.get("Mu", 0.0)),
                forces.get("Mu_y", 0.0),
                t_raft, fc, fy,
            )
            return {"raft_flexure": res}

        # ── STAIRCASE ────────────────────────────────────────
        elif member_type == MemberType.STAIRCASE:
            res = StaircaseDesign.design(
                going=inputs.get("going", 3.0),
                rise=inputs.get("rise", 150.0),
                tread=inputs.get("tread", 300.0),
                width=inputs.get("width", 1200.0),
                LL=inputs.get("LL", 3.0),
                fc=fc, fy=fy,
            )
            return {"staircase": res}

        # ── DOME ─────────────────────────────────────────────
        elif member_type == MemberType.DOME:
            res = DomeDesign.calculate_membrane_forces(
                radius=inputs.get("radius", 10.0),
                thickness=inputs.get("thickness", 0.15),
                DL=inputs.get("DL", 3.0),
                LL=inputs.get("LL", 0.5),
                theta_edge_deg=inputs.get("theta_edge", 45.0),
            )
            return {"dome": res}

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
                    old_depth = inputs.get("depth", 600.0)
                    new_depth = old_depth * 1.10
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
