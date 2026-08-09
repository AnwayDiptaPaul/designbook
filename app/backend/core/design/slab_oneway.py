# pyre-ignore-all-errors
import math
from backend.api.schemas.design_standards import SlabDesignInput, OneWaySlabForces, OneWaySlabResult

class OneWaySlabDesign:
    """One-way slab design per BNBC/ACI 318."""
    
    @staticmethod
    def design_flexure(inputs: SlabDesignInput, forces: OneWaySlabForces) -> OneWaySlabResult:
        """
        Designs a 1-meter strip of one-way slab.
        """
        b = 1000.0 # 1m strip
        d = inputs.thickness - inputs.cover - inputs.bar_dia / 2.0
        
        fc = inputs.material.fc
        fy = inputs.material.fy
        
        Mu_Nmm = forces.Mu * 1e6
        phi = 0.9
        
        Rn = Mu_Nmm / (phi * b * d**2)
        discriminant = 1 - 2 * Rn / (0.85 * fc)
        if discriminant < 0:
            return OneWaySlabResult(
                As_req_mm2_m=0.0,
                As_flexure_mm2_m=0.0,
                As_temp_mm2_m=0.0,
                status="FAIL - Section overstressed. Increase thickness.",
                s_max_mm=0.0,
                d_effective_mm=d,
            )
        
        rho_target = 0.85 * fc / fy * (1 - math.sqrt(discriminant))
        
        # Minimum flexural reinforcement (ACI 9.6.1)
        rho_flex_min = max(0.25 * math.sqrt(fc) / fy, 1.4 / fy)
        As_flexure = max(rho_target, rho_flex_min) * b * d
        
        # Temperature & shrinkage steel (ACI 24.4.3) — uses GROSS thickness
        rho_temp = 0.0018 if fy >= 420 else 0.0020
        As_temp = rho_temp * b * inputs.thickness
        
        As_req = max(As_flexure, As_temp)
        
        # Max spacing
        s_max = min(3 * inputs.thickness, 450)
        
        return OneWaySlabResult(
            As_req_mm2_m=float(As_req),
            As_flexure_mm2_m=float(As_flexure),
            As_temp_mm2_m=float(As_temp),
            s_max_mm=float(s_max),
            d_effective_mm=float(d),
            status="OK",
        )
