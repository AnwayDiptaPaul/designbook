# pyre-ignore-all-errors
import math
from typing import Dict, Any
from backend.api.schemas.design_standards import BeamDesignInput, BeamDesignForces, BeamFlexureResult, BeamShearResult

# Mathematical boundary guard (plan.md §Defensive Engineering)
EPSILON = 1e-9

class BeamDesign:
    """Design routines for rectangular and T-beams per BNBC 2020 / ACI 318-19."""
    
    @staticmethod
    def design_flexure(inputs: BeamDesignInput, forces: BeamDesignForces, phi: float = 0.9) -> BeamFlexureResult:
        """
        Calculates required tension reinforcement As for a singly reinforced rectangular section.
        """
        Mu_Nmm = forces.Mu * 1e6
        fc = inputs.material.fc
        fy = inputs.material.fy
        b = inputs.width
        d = inputs.depth - inputs.cover

        if b <= 0 or d <= 0:
            return BeamFlexureResult(
                As_req_mm2=0.0, rho=0.0, tension_controlled=False, 
                compression_reinforcement_needed=False, status="FAIL - Invalid Dimensions"
            )

        Rn = Mu_Nmm / (phi * b * d**2)
        
        discriminant = 1 - 2 * Rn / (0.85 * fc)
        if discriminant < 0:
            return BeamFlexureResult(
                As_req_mm2=0.0,
                status="FAIL - Section overstressed. Increase dimensions.",
                tension_controlled=False,
                compression_reinforcement_needed=True,
                rho=0.0
            )
            
        beta1 = max(0.65, min(0.85, 0.85 - 0.05 * (fc - 28) / 7))
        rho_target = 0.85 * fc / fy * (1 - math.sqrt(discriminant))
        
        rho_min = max(0.25 * math.sqrt(fc) / fy, 1.4 / fy)
        
        c = rho_target * fy / (0.85 * beta1 * fc) * d
        eps_t = 0.003 * (d - c) / max(c, EPSILON)
        
        is_tension_controlled = eps_t >= 0.005
        As_req = max(rho_target, rho_min) * b * d
        
        return BeamFlexureResult(
            As_req_mm2=float(As_req),
            rho=float(max(rho_target, rho_min)),
            tension_controlled=is_tension_controlled,
            compression_reinforcement_needed=not is_tension_controlled,
            status="OK" if is_tension_controlled else "WARN - Compression Reinforcement or Resize Needed"
        )
        
    @staticmethod
    def design_shear(inputs: BeamDesignInput, forces: BeamDesignForces, phi: float = 0.75) -> BeamShearResult:
        """
        Calculates required shear reinforcement spacing for a given bar size.
        """
        Vu_N = forces.Vu * 1000
        fc = inputs.material.fc
        fy_v = inputs.material.fy_v
        b = inputs.width
        d = inputs.depth - inputs.cover

        if b <= 0 or d <= 0:
             return BeamShearResult(status="FAIL - Invalid Dimensions")

        Vc = 0.17 * 1.0 * math.sqrt(fc) * b * d
        phi_Vc = phi * Vc
        
        if Vu_N <= 0.5 * phi_Vc:
            return BeamShearResult(status="No shear reinforcement required", Vs_req_kN=0)
            
        Vs_req = (Vu_N - phi_Vc) / phi
        
        Vs_max = 0.66 * math.sqrt(fc) * b * d
        if Vs_req > Vs_max:
             return BeamShearResult(status="Section too small. Enlarge section.", Vs_req_kN=Vs_req/1000, phi_Vc_kN=phi_Vc/1000)
             
        Av_over_s = Vs_req / max(fy_v * d, EPSILON) if Vs_req > 0 else 0
        
        return BeamShearResult(
            status="OK",
            phi_Vc_kN=float(phi_Vc / 1000),
            Vs_req_kN=float(Vs_req / 1000),
            Av_over_s_req=float(Av_over_s)
        )
