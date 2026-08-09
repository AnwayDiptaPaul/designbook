# pyre-ignore-all-errors
from backend.api.schemas.design_standards import RaftFoundationInput, RaftFoundationForces, TwoWaySlabResult

class RaftFoundationDesign:
    """Raft foundation design using Winkler Springs and FEA plate moments."""
    
    @staticmethod
    def design_flexure_fea(inputs: RaftFoundationInput, forces: RaftFoundationForces) -> TwoWaySlabResult:
        """
        Uses the exact same DDM/FEA extraction module as two-way slabs,
        but loaded with upward soil reaction springs.
        """
        from backend.core.design.slab_twoway import TwoWaySlabDesign
        from backend.api.schemas.design_standards import SlabDesignInput, TwoWaySlabForces
        
        slab_input = SlabDesignInput(
            thickness=inputs.thickness,
            cover=inputs.cover,
            bar_dia=20.0, # assumed
            material=inputs.material
        )
        slab_forces = TwoWaySlabForces(
            Mu_x=forces.Mu_x,
            Mu_y=forces.Mu_y
        )
        
        return TwoWaySlabDesign.design_flexure_fea(slab_input, slab_forces)
