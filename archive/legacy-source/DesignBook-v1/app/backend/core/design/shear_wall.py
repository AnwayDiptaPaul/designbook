import math

class ShearWallDesign:
    """Design routines for rectangular and flanged shear walls."""
    
    @staticmethod
    def design_shear(Vu: float, Pu: float, lw: float, hw: float, tw: float, fc: float, fy: float) -> dict:
        """
        Design for in-plane shear.
        Vu, Pu in kN. lw, hw, tw in mm.
        Returns horizontal and vertical web reinforcement.
        """
        Vu_N = Vu * 1000
        Pu_N = Pu * 1000
        
        # ACI Vc
        alpha_c = 0.25 if hw/lw <= 1.5 else 0.17 # Simplified interpolation stub
        lambda_f = 1.0
        
        # Vc = alpha_c * lambda * sqrt(fc) * tw * lw + (N_u * d) / (4 * l_w) 
        # But limited. For simplicity:
        Vc = alpha_c * lambda_f * math.sqrt(fc) * tw * lw + min(Pu_N / 4.0, 0.2 * fc * tw * lw)
        
        phi_Vc = 0.75 * Vc
        
        rho_t_min = 0.0025
        rho_l_min = 0.0025
        
        if Vu_N <= 0.5 * phi_Vc:
            return {"status": "OK", "rho_t": rho_t_min, "rho_l": rho_l_min}
            
        Vs_req = (Vu_N - phi_Vc) / 0.75
        
        Vs_max = 0.83 * math.sqrt(fc) * tw * lw
        if Vs_req > Vs_max:
            return {"status": "FAIL - Exceeds max shear", "rho_t": 0, "rho_l": 0}
            
        rho_t = Vs_req / (fy * tw * 0.8 * lw)
        rho_t = max(rho_t, rho_t_min)
        
        rho_l = max(rho_l_min, 0.0025 + 0.5 * (2.5 - hw/lw) * (rho_t - 0.0025))
        
        return {
            "status": "OK",
            "phi_Vc_kN": phi_Vc / 1000,
            "req_rho_t": rho_t,
            "req_rho_l": rho_l
        }

    @staticmethod
    def design_slender_wall(Pu: float, Mu: float, lw: float, hw: float, tw: float, fc: float, fy: float, As: float) -> dict:
        """
        Out-of-plane slender wall design per BNBC 2020 / ACI 318.
        Checks nominal moment capacity with axial load.
        """
        phi = 0.9
        a = (As * fy + Pu * 1000) / (0.85 * fc * lw)
        Mn = (As * fy + Pu * 1000) * (tw/2 - a/2) / 1e6 # kNm
        
        # P-Delta approximation (delta_s = 5 * M * L^2 / (48 * EI))
        # Simplified: check if Mn > Mu
        status = "OK" if phi * Mn > Mu else "Inadequate Moment Capacity"
        
        return {
            "phiMn_kNm": phi * Mn,
            "status": status
        }
