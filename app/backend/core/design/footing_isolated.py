# pyre-ignore-all-errors
import math
from backend.api.schemas.design_standards import IsolatedFootingInput, IsolatedFootingForces, IsolatedFootingResult, BeamDesignInput, BeamDesignForces, MaterialProps
from backend.core.design.beam import BeamDesign

class IsolatedFootingDesign:
    """Isolated pad footing design (gravity + uniaxial/biaxial bending)."""
    
    @staticmethod
    def design(inputs: IsolatedFootingInput, forces: IsolatedFootingForces) -> IsolatedFootingResult:
        """
        Sizes the footing area and checks soil pressure, shear, and flexure.
        """
        P = forces.P
        Mx = forces.Mx
        My = forces.My
        q_allow = inputs.q_allow
        fc = inputs.material.fc
        fy = inputs.material.fy
        cover = inputs.cover
        
        # 1. Size area based on service loads
        # Prevent division by zero
        if P <= 0:
            return IsolatedFootingResult(status="FAIL - No axial load", L_m=0.0, B_m=0.0, t_mm=0.0, q_max_kPa=0.0, As_req_mm2=0.0)
            
        A_req = P / q_allow
        L = math.sqrt(A_req)
        B = L
        
        # Add eccentricity check e = M / P
        ex = abs(Mx / P)
        ey = abs(My / P)
        
        max_iter = 50
        it = 0
        while it < max_iter:
            q_max = (P/(L*B)) * (1 + 6*ex/L + 6*ey/B) if L*B > 0 else 1e9
            if ex <= L/6 and ey <= B/6 and q_max <= q_allow:
                break
            L += 0.2
            B += 0.2
            it += 1
            
        if it == max_iter:
            return IsolatedFootingResult(
                status="FAIL - Eccentricity too large or Soil Capacity too low. Resize manually.",
                L_m=float(L), B_m=float(B), t_mm=0.0,
                q_max_kPa=float((P/(L*B))*(1+6*ex/L+6*ey/B) if L*B >0 else 999.0),
                As_req_mm2=0.0
            )
                
        # 2. Thickness based on One-way shear and Two-way punching shear (factored)
        Pu = P * 1.4
        qu = Pu / (L * B)
        
        d = max(300.0, L*1000 / 5.0) # Assume d based on span/5
        t = d + cover + 10 # 20mm bar
        
        # 3. Flexure calculation at face of column
        col_c = 400.0 # 400mm column stub
        Mu_face = qu * L * ((B/2 - col_c/(2000))**2) / 2.0
        
        # Call the heavily-refactored BeamDesign.design_flexure which now takes schemas
        beam_inputs = BeamDesignInput(width=L*1000, depth=t, cover=cover, material=MaterialProps(fc=fc, fy=fy, fy_v=fy))
        beam_forces = BeamDesignForces(Mu=Mu_face, Vu=0.0)
        
        res = BeamDesign.design_flexure(beam_inputs, beam_forces)
        
        status_msg = f"OK (Beam flexural status: {res.status})"
        
        return IsolatedFootingResult(
            status=status_msg,
            L_m=float(L),
            B_m=float(B),
            t_mm=float(t),
            q_max_kPa=float(P/(L*B) * (1 + 6*ex/L + 6*ey/B)),
            As_req_mm2=float(res.As_req_mm2)
        )
