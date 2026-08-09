class RaftFoundationDesign:
    """Raft foundation design using Winkler Springs and FEA plate moments."""
    
    @staticmethod
    def design_flexure_fea(Mu_x: float, Mu_y: float, t: float, fc: float, fy: float) -> dict:
        """
        Uses the exact same DDM/FEA extraction module as two-way slabs,
        but loaded with upward soil reaction springs.
        """
        from .slab_twoway import TwoWaySlabDesign
        return TwoWaySlabDesign.design_flexure_fea(Mu_x, Mu_y, t, fc, fy, cover=75)
