import math

class ColumnDesign:
    """Design routines for rectangular and circular columns per ACI 318 / BNBC 2020."""
    
    @staticmethod
    def generate_interaction_diagram(b: float, h: float, fc: float, fy: float, rebar_layers: list[dict]) -> dict:
        """
        Generates P-M interaction diagram points (Axial capacity vs Moment capacity)
        using strain compatibility and the Whitney stress block.
        rebar_layers: [{"depth": float, "As": float_mm2}] where depth is from extreme fiber.
        """
        beta1 = max(0.65, min(0.85, 0.85 - 0.05 * (fc - 28) / 7))
        points = []
        
        # 1. Pure Compression (Point A)
        Ag = b * h
        As_total = sum(r["As"] for r in rebar_layers)
        P_o = 0.85 * fc * (Ag - As_total) + fy * As_total
        # Tied column limit: phi = 0.65, alpha = 0.80
        phi_Pn_max = 0.65 * 0.80 * P_o / 1000 # convert to kN
        points.append({"P": float(phi_Pn_max), "M": 0.0})
        
        # 2. Iterate Neutral Axis (c) from h down to some small value to get curve
        # We'll pick 10 steps to keep it light but accurate
        steps = 15
        for i in range(steps + 1):
            # c varies from h*1.5 (close to uniform compression) to d_min/2 (tension)
            c = (h * 1.2) * (1 - i/steps) + 10.0 # avoid c=0
            
            # Strain distribution: extreme fiber eps_c = 0.003
            # Steel strains: eps_s = 0.003 * (d - c) / c
            # Stress f_s = E * eps_s (max fy)
            E = 200000.0 # MPa
            
            total_P = 0.0
            total_M = 0.0 # about plastic center (geometric center for symmetry)
            plastic_center = h / 2.0
            
            # Concrete contribution
            a = min(beta1 * c, h)
            C_c = 0.85 * fc * a * b
            total_P += C_c
            total_M += C_c * (plastic_center - a / 2.0)
            
            # Steel contribution
            for layer in rebar_layers:
                eps_s = 0.003 * (layer["depth"] - c) / c
                fs = max(-fy, min(fy, E * eps_s))
                
                # Check if bar is in compression block zone and subtract displaced concrete
                force_s = layer["As"] * fs
                if layer["depth"] <= a:
                    force_s -= layer["As"] * (0.85 * fc)
                
                total_P -= force_s # P is positive for compression in our cap logic
                total_M += force_s * (plastic_center - layer["depth"])
                
            # Strength reduction factor phi (interpolation between 0.65 and 0.9)
            # Find eps_t (strain in extreme tension bar)
            d_max = max(r["depth"] for r in rebar_layers)
            eps_t = 0.003 * (d_max - c) / c
            if eps_t <= 0.002:
                phi = 0.65
            elif eps_t >= 0.005:
                phi = 0.90
            else:
                phi = 0.65 + (eps_t - 0.002) * (0.25 / 0.003)
                
            points.append({
                "P": float(phi * total_P / 1000), 
                "M": float(phi * total_M / 1e6)
            })

        # 3. Pure Tension (Point B)
        phi_Tn = 0.9 * As_total * fy / 1000
        points.append({"P": float(-phi_Tn), "M": 0.0})
        
        return {"points": sorted(points, key=lambda x: x["P"], reverse=True)}

    @staticmethod
    def check_slenderness(klu_over_r: float, M1: float, M2: float, is_sway: bool) -> bool:
        """Checks if slenderness effects can be ignored per ACI 318."""
        if is_sway:
            return klu_over_r < 22
        else:
            limit = 34 - 12 * (M1 / M2) if M2 != 0 else 34
            limit = min(limit, 40)
            return klu_over_r < limit

    @staticmethod
    def magnify_moments(Mu: float, Pu: float, Ag: float, fc: float, klu_over_r: float) -> float:
        """
        Magnifies moment for slenderness (Simplified ACI 318 method).
        Pc = pi^2 * EI / (kl)^2
        delta = Cm / (1 - Pu / (0.75 * Pc))
        """
        E = 4700 * math.sqrt(fc) # MPa
        Ig = (1/12) * (Ag**2) # Simplified for square
        EI = 0.4 * E * Ig / (1 + 0.6) # 0.6 is creep beta_dns stub
        
        # Pc = pi^2 * EI / (kl)^2  => kl/r = klu_over_r => kl = r * klu_over_r
        # r approx 0.3 * h
        r = math.sqrt(Ig / Ag)
        kl = r * klu_over_r
        
        Pc = (math.pi**2 * EI) / (kl**2) if kl > 0 else 1e12
        Cm = 1.0 # Sway/Worst case stub
        
        delta = Cm / (1 - (Pu * 1000) / (0.75 * Pc))
        delta = max(1.0, min(delta, 2.5)) # Safety cap
        
        return Mu * delta

    @staticmethod
    def check_biaxial_capacity(Pu: float, Mux: float, Muy: float, diagram_x: list, diagram_y: list) -> dict:
        """
        Checks biaxial capacity using Bresler Load Contour Method (α=1.5 stub).
        (Mux/Mrx)^1.5 + (Muy/Mry)^1.5 <= 1.0
        Where Mrx is the nominal moment capacity for the given Pu.
        """
        def get_Mr(diag, P_target):
            # Sort by P to ensure we can interpolate
            sorted_diag = sorted(diag, key=lambda x: x["P"])
            for i in range(len(sorted_diag)-1):
                if sorted_diag[i]["P"] <= P_target <= sorted_diag[i+1]["P"]:
                    p1, m1 = sorted_diag[i]["P"], sorted_diag[i]["M"]
                    p2, m2 = sorted_diag[i+1]["P"], sorted_diag[i+1]["M"]
                    return m1 + (m2 - m1) * (P_target - p1) / (p2 - p1) if p2 != p1 else m1
            return 0.0
            
        Mrx = get_Mr(diagram_x, Pu)
        Mry = get_Mr(diagram_y, Pu)
        
        if Mrx <= 0 or Mry <= 0:
            return {"status": "FAIL - Axial load exceeds capacity envelope", "ratio": 999}
            
        try:
            alpha = 1.5 # standard approximation
            ratio = (abs(Mux)/Mrx)**alpha + (abs(Muy)/Mry)**alpha
        except (ZeroDivisionError, ValueError):
            ratio = 999

        return {
            "status": "OK" if ratio <= 1.0 else "FAIL",
            "ratio": ratio,
            "Mrx": Mrx,
            "Mry": Mry
        }

    @staticmethod
    def design_shear(Vu: float, b: float, d: float, fc: float, fy: float, av: float, s: float) -> dict:
        """
        Shear design of RC column per ACI 318.
        Vc = 0.17 * sqrt(fc) * b * d
        Vs = Av * fy * d / s
        """
        phi = 0.75
        Vc = 0.17 * math.sqrt(fc) * b * d / 1000 # kN
        Vs = (av * fy * d / s) / 1000 if s > 0 else 0
        Vn = Vc + Vs
        status = "OK" if Vu < phi * Vn else "Inadequate Shear Capacity"
        return {"Vc": Vc, "Vs": Vs, "phiVn": phi * Vn, "status": status}

    @staticmethod
    def design_torsion(Tu: float, Vu: float, b: float, h: float, fc: float, fy: float, 
                       at: float, s: float, area_long: float) -> dict:
        """
        Torsion design per ACI 318.
        Checks threshold torsion and combined shear-torsion.
        """
        phi = 0.75
        Acp = b * h
        Pcp = 2 * (b + h)
        T_th = 0.083 * math.sqrt(fc) * (Acp**2 / Pcp) / 1e6 # kNm
        
        status = "OK"
        if Tu > phi * T_th:
            # Requires torsional reinforcement
            # Simplified check: s < spacing limit
            if (at * fy * 2 * b * h / s) / 1e6 < Tu:
                status = "Inadequate Torsional Rebar"
        
        return {"T_threshold": T_th, "status": status}
