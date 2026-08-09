import math

class FlatPlateDesign:
    """Beamless slab (flat plate) and punching shear checks."""
    
    @staticmethod
    def check_punching_shear(Vu: float, Mu_unbalanced: float, c1: float, c2: float, d: float, fc: float, location: str = "interior") -> dict:
        """
        Punching shear capacity of two-way slabs at columns.
        Vu in kN, Mu in kN-m, dimensions in mm.
        """
        # Critical perimeter b0
        if location == "interior":
            b0 = 2 * (c1 + d) + 2 * (c2 + d)
            alpha_s = 40
        elif location == "edge":
            b0 = 2 * (c1 + d/2) + (c2 + d)
            alpha_s = 30
        else: # corner
            b0 = (c1 + d/2) + (c2 + d/2)
            alpha_s = 20
            
        beta_ratio = max(c1, c2) / min(c1, c2)
        
        Vu_N = Vu * 1000
        
        # 3 ACI equations for Vc
        vc1 = 0.33 * math.sqrt(fc)
        vc2 = 0.17 * (1 + 2/beta_ratio) * math.sqrt(fc)
        vc3 = 0.083 * (alpha_s * d / b0 + 2) * math.sqrt(fc)
        
        vc_allowable = min(vc1, vc2, vc3)
        phi_Vc = 0.75 * vc_allowable * b0 * d / 1000 # in kN
        
        # Note: Unbalanced moment shear stress (gamma_v * Mu * c / Jc) is simplified here.
        # In a full implementation, the polar moment Jc is computed.
        # Here we just check direct shear for phase 6 stub.
        
        status = "OK" if Vu <= phi_Vc else "FAIL - Increase thickness or add shear studs"
        
        return {
            "status": status,
            "b0_mm": b0,
            "phi_Vc_kN": phi_Vc,
            "Vu_kN": Vu
        }

    @staticmethod
    def design_pt_slab(P_eff: float, sag: float, span: float, dead_load: float) -> dict:
        """
        Calculates equivalent upward load from PT tendon profile.
        P_eff: effectivce force (kN), sag: tendon drape (m), span (m), dead_load (kN/m)
        """
        w_up = 8 * P_eff * sag / (span**2)
        net_load = dead_load - w_up
        return {"w_up": w_up, "net_load": net_load}

    @staticmethod
    def check_stresses(P: float, M: float, A: float, Z: float, fc: float) -> dict:
        """
        Checks concrete stresses at service (MPa). 
        P (kN), M (kNm), A (mm2), Z (mm3)
        """
        f_top = (P * 1000 / A) - (M * 1e6 / Z)
        f_bot = (P * 1000 / A) + (M * 1e6 / Z)
        
        # ACI limits: fc' = 35 MPa, ft_limit = 0.5 * sqrt(fc)
        ft_limit = 0.5 * math.sqrt(fc)
        fc_limit = 0.45 * fc
        
        status = "OK"
        if f_top > fc_limit or f_bot > fc_limit:
            status = "FAIL - Compression Exceeded"
        if f_top < -ft_limit or f_bot < -ft_limit:
            status = "FAIL - Tension Exceeded (Cracked)"
            
        return {"f_top": f_top, "f_bot": f_bot, "status": status}
