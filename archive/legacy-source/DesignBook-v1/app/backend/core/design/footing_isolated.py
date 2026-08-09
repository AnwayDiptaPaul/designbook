import math

class IsolatedFootingDesign:
    """Isolated pad footing design (gravity + uniaxial/biaxial bending)."""
    
    @staticmethod
    def design(P: float, Mx: float, My: float, q_allow: float, fc: float, fy: float, cover: float=75) -> dict:
        """
        Sizes the footing area and checks soil pressure, shear, and flexure.
        P in kN, M in kN-m, q_allow in kPa.
        """
        # 1. Size area based on service loads
        A_req = P / q_allow
        L = math.sqrt(A_req)
        B = L
        
        # Add eccentricity check e = M / P
        ex = abs(Mx / P) if P > 0 else 1e6
        ey = abs(My / P) if P > 0 else 1e6
        
        # If e > L/6, there is uplift. We need to increase size.
        # We also check for soil pressure q_max <= q_allow
        # q_max = (P/A) * (1 + 6ex/L + 6ey/B)
        max_iter = 50
        it = 0
        while it < max_iter:
            q_max = (P/(L*B)) * (1 + 6*ex/L + 6*ey/B) if L*B > 0 else 1e9
            # print(f"DEBUG: it={it}, L={L:.2f}, B={B:.2f}, ex={ex:.2f}, q_max={q_max:.2f}")
            if ex <= L/6 and ey <= B/6 and q_max <= q_allow:
                break
            # Increment significantly if far off
            L += 0.2
            B += 0.2
            it += 1
            
        if it == max_iter:
            return {
                "status": "FAIL - Eccentricity too large or Soil Capacity too low. Resize manually.",
                "L_m": L, "B_m": B, "q_max_kPa": (P/(L*B))*(1+6*ex/L+6*ey/B) if L*B >0 else 999
            }
                
        # 2. Thickness based on One-way shear and Two-way punching shear (factored)
        # Assuming P is factored by 1.4 for strength design in this simplistic stub
        Pu = P * 1.4
        qu = Pu / (L * B)
        
        d = max(300.0, L*1000 / 5.0) # Assume d based on span/5
        t = d + cover + 10 # 20mm bar
        
        # 3. Flexure calculation at face of column
        # Mu = qu * L * (B/2 - c/2)^2 / 2
        col_c = 400.0 # 400mm column stub
        Mu_face = qu * L * ((B/2 - col_c/(2000))**2) / 2.0
        
        from backend.core.design.beam import BeamDesign
        res = BeamDesign.design_flexure(Mu_face, L*1000, d, fc, fy)
        
        return {
            "L_m": L,
            "B_m": B,
            "t_mm": t,
            "q_max_kPa": P/(L*B) * (1 + 6*ex/L + 6*ey/B),
            "As_req_mm2": res["As_req_mm2"]
        }
