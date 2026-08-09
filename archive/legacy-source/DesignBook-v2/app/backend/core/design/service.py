from typing import Any, Dict
from backend.models.member import MemberType
from backend.core.design.beam import BeamDesign
from backend.core.design.column import ColumnDesign
from backend.core.design.slab_beamless import FlatPlateDesign
from backend.core.design.shear_wall import ShearWallDesign
from backend.core.design.retaining_wall import RetainingWallDesign, RetainingWallInput
from backend.core.design.pile import PileDesign
from backend.core.design.cfs import CFSDesign

class StructuralDesignService:
    """Unified service for structural member design dispatch."""
    
    @staticmethod
    def design_member(member_type: MemberType, inputs: Dict[str, Any], forces: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches design to the appropriate module based on member type."""
        
        fc = inputs.get("fc", 25.0)
        fy = inputs.get("fy", 500.0)
        b = inputs.get("width", 300.0)
        h = inputs.get("depth", 600.0)
        d = h - 60.0 # Effective depth estimate
        
        if member_type == MemberType.BEAM:
            flexure = BeamDesign.design_flexure(forces.get("Mu", 0.0), b, d, fc, fy)
            shear = BeamDesign.design_shear(forces.get("Vu", 0.0), b, d, fc, fy)
            return {"flexure": flexure, "shear": shear}
            
        elif member_type == MemberType.COLUMN:
            Pu = forces.get("Pu", 0.0)
            Mu = forces.get("Mu", 0.0)
            # Standard RC column design
            rebar_layers = inputs.get("rebar_layers", [{"depth": 50, "As": 400}, {"depth": h-50, "As": 400}])
            diag = ColumnDesign.generate_interaction_diagram(b, h, fc, fy, rebar_layers)
            shear = ColumnDesign.design_shear(forces.get("Vu", 0.0), b, d, fc, fy, 400, 150)
            return {"interaction_diagram": diag, "shear": shear}
            
        elif member_type == MemberType.SLAB:
            if inputs.get("is_pt", False):
                L = inputs.get("span", 6.0)
                W = forces.get("total_load", 10.0)
                P_pt = inputs.get("pt_force", 1000.0)
                check = FlatPlateDesign.check_stresses(L, b, h, P_pt, 0.1, W)
                return {"pt_check": check}
            return {"status": "Standard RC slab design not yet active"}
            
        elif member_type == MemberType.SHEAR_WALL:
            Mu = forces.get("Mu", 0.0)
            Pu = forces.get("Pu", 0.0)
            lw = inputs.get("width", 1000.0) # For walls, width is length lw
            tw = inputs.get("thickness", 300.0)
            hw = inputs.get("height", 3500.0)
            # Slender wall check: design_slender_wall(Pu, Mu, lw, hw, tw, fc, fy, As)
            res = ShearWallDesign.design_slender_wall(Pu, Mu, lw, hw, tw, fc, fy, 800.0)
            return {"slender_wall_check": res}

        elif member_type == MemberType.FOOTING:
            # Could map to RetainingWall or Pile if specialized
            return {"status": "Footing design stub"}
            
        return {"status": "Unknown member type or design logic pending"}
