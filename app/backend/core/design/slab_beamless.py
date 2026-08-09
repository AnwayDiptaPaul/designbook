# pyre-ignore-all-errors
import math
from backend.api.schemas.design_standards import PunchingShearInput, PunchingShearResult, PTSlabInput, PTLoadResult, StripStressInput, StripStressResult

class FlatPlateDesign:
    """Beamless slab (flat plate) and punching shear checks."""
    
    @staticmethod
    def check_punching_shear(inputs: PunchingShearInput, d: float, fc: float) -> PunchingShearResult:
        """
        Punching shear capacity of two-way slabs at columns.
        """
        location = inputs.location
        c1 = inputs.c1
        c2 = inputs.c2
        Vu = inputs.Vu
        
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
            
        beta_ratio = max(c1, c2) / (min(c1, c2) or 1.0)
        
        # 3 ACI equations for Vc
        vc1 = 0.33 * math.sqrt(fc)
        vc2 = 0.17 * (1 + 2/beta_ratio) * math.sqrt(fc)
        vc3 = 0.083 * (alpha_s * d / b0 + 2) * math.sqrt(fc)
        
        vc_allowable = min(vc1, vc2, vc3)
        phi_Vc = 0.75 * vc_allowable * b0 * d / 1000 # in kN
        
        status = "OK" if Vu <= phi_Vc else "FAIL - Increase thickness or add shear studs"
        
        return PunchingShearResult(
            status=status,
            b0_mm=float(b0),
            phi_Vc_kN=float(phi_Vc),
            Vu_kN=float(Vu)
        )

    @staticmethod
    def design_pt_slab(inputs: PTSlabInput) -> PTLoadResult:
        """
        Calculates equivalent upward load from PT tendon profile.
        """
        w_up = 8 * inputs.P_eff * inputs.sag / (inputs.span**2)
        net_load = inputs.dead_load - w_up
        return PTLoadResult(w_up=float(w_up), net_load=float(net_load))

    @staticmethod
    def check_stresses(inputs: StripStressInput, fc: float) -> StripStressResult:
        """
        Checks concrete stresses at service (MPa). 
        """
        f_top = (inputs.P * 1000 / inputs.A) - (inputs.M * 1e6 / inputs.Z)
        f_bot = (inputs.P * 1000 / inputs.A) + (inputs.M * 1e6 / inputs.Z)
        
        # ACI limits: fc' = 35 MPa, ft_limit = 0.5 * sqrt(fc)
        ft_limit = 0.5 * math.sqrt(fc)
        fc_limit = 0.45 * fc
        
        status = "OK"
        if f_top > fc_limit or f_bot > fc_limit:
            status = "FAIL - Compression Exceeded"
        if f_top < -ft_limit or f_bot < -ft_limit:
            status = "FAIL - Tension Exceeded (Cracked)"
            
        return StripStressResult(f_top=float(f_top), f_bot=float(f_bot), status=status)
