import math

class OneWaySlabDesign:
    """One-way slab design per BNBC/ACI 318."""
    
    @staticmethod
    def design_flexure(Mu: float, t: float, fc: float, fy: float, cover: float = 20, bar_dia: float = 10) -> dict:
        """
        Designs a 1-meter strip of one-way slab.
        Mu in kN-m, t in mm.
        Returns required As in mm^2/m.
        """
        b = 1000.0 # 1m strip
        d = t - cover - bar_dia / 2.0
        
        Mu_Nmm = Mu * 1e6
        phi = 0.9
        
        Rn = Mu_Nmm / (phi * b * d**2)
        rho_target = 0.85 * fc / fy * (1 - math.sqrt(1 - 2 * Rn / (0.85 * fc)))
        
        # Temperature & shrinkage minimum
        rho_min = 0.0018 if fy >= 420 else 0.0020
        
        As_req = max(rho_target, rho_min) * b * t
        
        # Max spacing
        s_max = min(3 * t, 450)
        
        return {
            "As_req_mm2_m": As_req,
            "s_max_mm": s_max,
            "d_effective_mm": d
        }
