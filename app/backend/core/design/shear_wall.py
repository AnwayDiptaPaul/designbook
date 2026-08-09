# pyre-ignore-all-errors
import math
from backend.api.schemas.design_standards import ShearWallInput, ShearWallForces, ShearWallShearResult, SlenderWallInput, SlenderWallResult

class ShearWallDesign:
    """Design routines for rectangular and flanged shear walls."""
    
    @staticmethod
    def design_shear(inputs: ShearWallInput, forces: ShearWallForces) -> ShearWallShearResult:
        """
        Design for in-plane shear.
        """
        Vu_N = forces.Vu * 1000
        Pu_N = forces.Pu * 1000
        
        tw = inputs.tw
        lw = inputs.lw
        hw = inputs.hw
        fc = inputs.material.fc
        fy = inputs.material.fy
        
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
            return ShearWallShearResult(status="OK", phi_Vc_kN=float(phi_Vc / 1000), req_rho_t=rho_t_min, req_rho_l=rho_l_min)
            
        Vs_req = (Vu_N - phi_Vc) / 0.75
        
        Vs_max = 0.83 * math.sqrt(fc) * tw * lw
        if Vs_req > Vs_max:
            return ShearWallShearResult(status="FAIL - Exceeds max shear", phi_Vc_kN=float(phi_Vc / 1000), req_rho_t=0.0, req_rho_l=0.0)
            
        rho_t = Vs_req / (fy * tw * 0.8 * lw)
        if rho_t < rho_t_min:
            rho_t = rho_t_min
            
        rho_l = max(rho_l_min, 0.0025 + 0.5 * (2.5 - hw/lw) * (rho_t - 0.0025))
        
        return ShearWallShearResult(
            status="OK",
            phi_Vc_kN=float(phi_Vc / 1000),
            req_rho_t=float(rho_t),
            req_rho_l=float(rho_l)
        )

    @staticmethod
    def design_slender_wall(inputs: SlenderWallInput, Mu: float, Pu: float) -> SlenderWallResult:
        """
        Out-of-plane slender wall design per BNBC 2020 / ACI 318.
        Checks nominal moment capacity with axial load.
        """
        phi = 0.9
        lw = inputs.lw
        tw = inputs.tw
        As = inputs.As
        fc = inputs.material.fc
        fy = inputs.material.fy
        
        a = (As * fy + Pu * 1000) / (0.85 * fc * lw)
        Mn = (As * fy + Pu * 1000) * (tw/2 - a/2) / 1e6 # kNm
        
        # P-Delta approximation (delta_s = 5 * M * L^2 / (48 * EI))
        # Simplified: check if Mn > Mu
        status = "OK" if phi * Mn > Mu else "Inadequate Moment Capacity"
        
        return SlenderWallResult(
            phiMn_kNm=float(phi * Mn),
            status=status
        )
