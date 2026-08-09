import math

class StaircaseDesign:
    """Design routines for Dog-legged staircases."""
    
    @staticmethod
    def design(going: float, rise: float, tread: float, width: float, LL: float, fc: float, fy: float) -> dict:
        """
        Span = going + landing.
        Calculates waist slab thickness and main flexural reinforcements.
        """
        span = going + 1.2 # assume 1.2m landing
        
        # Required waist t
        t = span * 1000 / 25.0
        d = t - 20 - 6 # cover + half bar
        
        # Loading
        dead_waist = (t/1000) * 24.0 * math.sqrt(rise**2 + tread**2)/tread
        dead_steps = (rise/1000) / 2.0 * 24.0
        DL = dead_waist + dead_steps + 1.5 # SDL
        
        wu = 1.2 * DL + 1.6 * LL
        
        Mu = wu * span**2 / 8.0
        
        from backend.core.design.beam import BeamDesign
        res = BeamDesign.design_flexure(Mu, 1000.0, d, fc, fy)
        
        return {
            "waist_slab_t_mm": t,
            "design_load_wu_kPa": wu,
            "Mu_kNm_m": Mu,
            "As_req_mm2_m": res["As_req_mm2"]
        }
