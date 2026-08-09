import math

class BeamDesign:
    """Design routines for rectangular and T-beams per BNBC 2020 / ACI 318-19."""
    
    @staticmethod
    def design_flexure(Mu: float, b: float, d: float, fc: float, fy: float, phi: float = 0.9) -> dict:
        """
        Calculates required tension reinforcement As for a singly reinforced rectangular section.
        Mu in kN-m, b and d in mm, fc and fy in MPa.
        Returns As_req in mm^2, and checks if section is compression controlled.
        """
        # Mu = phi * As * fy * (d - a/2), where a = As*fy / (0.85*fc*b)
        # Mu = phi * rho * b * d^2 * fy * (1 - 0.59*rho*fy/fc)  <-- using Rn method
        Mu_Nmm = Mu * 1e6
        Rn = Mu_Nmm / (phi * b * d**2)
        
        # Check if Rn exceeds max theoretical limit (0.85*fc / 2 is approx limit for sqrt)
        discriminant = 1 - 2 * Rn / (0.85 * fc)
        if discriminant < 0:
            return {
                "As_req_mm2": 0,
                "status": "FAIL - Section overstressed. Increase dimensions.",
                "tension_controlled": False,
                "compression_reinforcement_needed": True
            }
            
        beta1 = max(0.65, min(0.85, 0.85 - 0.05 * (fc - 28) / 7))
        rho_target = 0.85 * fc / fy * (1 - math.sqrt(discriminant))
        
        rho_min = max(0.25 * math.sqrt(fc) / fy, 1.4 / fy)
        
        c = rho_target * fy / (0.85 * beta1 * fc) * d
        eps_t = 0.003 * (d - c) / (c if c > 0 else 0.001)
        
        is_tension_controlled = eps_t >= 0.005
        
        As_req = max(rho_target, rho_min) * b * d
        
        return {
            "As_req_mm2": As_req,
            "rho": max(rho_target, rho_min),
            "tension_controlled": is_tension_controlled,
            "compression_reinforcement_needed": not is_tension_controlled,
            "status": "OK" if is_tension_controlled else "WARN - Compression Reinforcement or Resize Needed"
        }
        
    @staticmethod
    def design_shear(Vu: float, b: float, d: float, fc: float, fy_vt: float, phi: float = 0.75) -> dict:
        """
        Calculates required shear reinforcement spacing for a given bar size.
        Vu in kN.
        """
        Vu_N = Vu * 1000
        # Vc = 0.17 * lambda * sqrt(fc) * b * d
        Vc = 0.17 * 1.0 * math.sqrt(fc) * b * d
        
        phi_Vc = phi * Vc
        
        if Vu_N <= 0.5 * phi_Vc:
            return {"status": "No shear reinforcement required", "Vs_req": 0}
            
        Vs_req = (Vu_N - phi_Vc) / phi
        
        # Check max Vs
        Vs_max = 0.66 * math.sqrt(fc) * b * d
        if Vs_req > Vs_max:
             return {"status": "Section too small. Enlarge section.", "Vs_req": Vs_req}
             
        # Required Av/s (mm^2/mm)
        # Vs = (Av * fy_vt * d) / s  =>  Av/s = Vs / (fy_vt * d)
        Av_over_s = Vs_req / (fy_vt * d) if Vs_req > 0 else 0
        
        return {
            "status": "OK",
            "phi_Vc_kN": phi_Vc / 1000,
            "Vs_req_kN": Vs_req / 1000,
            "Av_over_s_req": Av_over_s
        }
