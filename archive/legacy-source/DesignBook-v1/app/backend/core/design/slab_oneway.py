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
        discriminant = 1 - 2 * Rn / (0.85 * fc)
        if discriminant < 0:
            return {
                "As_req_mm2_m": 0,
                "As_flexure_mm2_m": 0,
                "As_temp_mm2_m": 0,
                "status": "FAIL - Section overstressed. Increase thickness.",
                "s_max_mm": 0,
                "d_effective_mm": d,
            }
        
        rho_target = 0.85 * fc / fy * (1 - math.sqrt(discriminant))
        
        # Minimum flexural reinforcement (ACI 9.6.1)
        rho_flex_min = max(0.25 * math.sqrt(fc) / fy, 1.4 / fy)
        As_flexure = max(rho_target, rho_flex_min) * b * d
        
        # Temperature & shrinkage steel (ACI 24.4.3) — uses GROSS thickness
        rho_temp = 0.0018 if fy >= 420 else 0.0020
        As_temp = rho_temp * b * t
        
        As_req = max(As_flexure, As_temp)
        
        # Max spacing
        s_max = min(3 * t, 450)
        
        return {
            "As_req_mm2_m": As_req,
            "As_flexure_mm2_m": As_flexure,
            "As_temp_mm2_m": As_temp,
            "s_max_mm": s_max,
            "d_effective_mm": d,
            "status": "OK",
        }
