import math


class ColumnDesign:
    """Design routines for rectangular and circular columns per ACI 318 / BNBC 2020."""

    @staticmethod
    def generate_interaction_diagram(
        b: float, h: float, fc: float, fy: float, rebar_layers: list[dict]
    ) -> dict:
        """
        Generates P-M interaction diagram points using strain compatibility
        and the Whitney stress block.

        rebar_layers: [{"depth": float_mm, "As": float_mm2}]
            depth = distance from the COMPRESSION face to the bar centroid.

        Returns capacities using the convention:
            P positive = compression, M positive = capacity (always >= 0).
        Units:  P in kN, M in kN-m.
        """
        beta1 = max(0.65, min(0.85, 0.85 - 0.05 * (fc - 28) / 7))
        points = []

        Ag = b * h  # mm²
        As_total = sum(r["As"] for r in rebar_layers)
        E_s = 200_000.0  # MPa

        # ── 1. Pure Compression (max tied column capacity) ───────────
        P_o = 0.85 * fc * (Ag - As_total) + fy * As_total  # N
        phi_Pn_max = 0.65 * 0.80 * P_o / 1000  # kN
        points.append({"P": float(phi_Pn_max), "M": 0.0})

        # ── 2. Sweep neutral axis c from ~1.5h down to near zero ─────
        n_steps = 20
        d_max = max(r["depth"] for r in rebar_layers)

        for i in range(n_steps + 1):
            frac = i / n_steps  # 0 → 1
            c = h * 1.5 * (1 - frac) + 5.0  # avoid c = 0

            # Concrete compression block
            a = min(beta1 * c, h)
            Cc = 0.85 * fc * a * b  # N  (compression +)

            plastic_center = h / 2.0  # take moments about geometric center

            # Concrete contribution to P and M
            P_conc = Cc
            M_conc = Cc * (plastic_center - a / 2.0)

            # Steel contributions
            P_steel = 0.0
            M_steel = 0.0
            for layer in rebar_layers:
                eps_s = 0.003 * (layer["depth"] - c) / c
                fs = max(-fy, min(fy, E_s * eps_s))

                F_s = layer["As"] * fs  # N  (+ = tension, − = compression)

                # Subtract displaced concrete if bar is inside stress block
                if layer["depth"] <= a:
                    F_s -= layer["As"] * 0.85 * fc  # reduce tension / increase compression

                P_steel -= F_s  # compression positive convention
                M_steel += F_s * (layer["depth"] - plastic_center)

            total_P = P_conc + P_steel  # N
            total_M = M_conc + M_steel  # N-mm

            # Strength-reduction factor φ (ACI 318-19 §21.2.2)
            eps_t = 0.003 * (d_max - c) / c
            if eps_t <= 0.002:
                phi = 0.65
            elif eps_t >= 0.005:
                phi = 0.90
            else:
                phi = 0.65 + (eps_t - 0.002) * (0.25 / 0.003)

            points.append({
                "P": float(phi * total_P / 1000),   # kN
                "M": float(abs(phi * total_M / 1e6)),  # kN-m (always +)
            })

        # ── 3. Pure Tension ──────────────────────────────────────────
        phi_Tn = 0.9 * As_total * fy / 1000  # kN
        points.append({"P": float(-phi_Tn), "M": 0.0})

        return {"points": sorted(points, key=lambda x: x["P"], reverse=True)}

    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    def check_slenderness(klu_over_r: float, M1: float, M2: float, is_sway: bool) -> bool:
        """Checks if slenderness effects can be ignored per ACI 318."""
        if is_sway:
            return klu_over_r < 22
        else:
            limit = 34 - 12 * (M1 / M2) if M2 != 0 else 34
            limit = min(limit, 40)
            return klu_over_r < limit

    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    def magnify_moments(
        Mu: float, Pu: float, b: float, h: float, fc: float,
        klu_over_r: float, beta_dns: float = 0.6,
    ) -> float:
        """
        Magnifies moment for slenderness (Simplified ACI 318 method).

        b, h in mm; Pu in kN; Mu in kN-m; fc in MPa.
        """
        Ec = 4700 * math.sqrt(fc)  # MPa
        Ig = b * h**3 / 12  # mm⁴
        Ag = b * h
        EI = 0.4 * Ec * Ig / (1 + beta_dns)

        r = math.sqrt(Ig / Ag)
        kl = r * klu_over_r  # mm

        Pc = (math.pi**2 * EI) / (kl**2) if kl > 0 else 1e12  # N
        Cm = 1.0

        delta = Cm / (1 - (Pu * 1000) / (0.75 * Pc))
        delta = max(1.0, min(delta, 2.5))

        return Mu * delta

    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    def check_biaxial_capacity(
        Pu: float, Mux: float, Muy: float,
        diagram_x: list, diagram_y: list,
    ) -> dict:
        """
        Bresler Load Contour Method for biaxial bending.
        (Mux / Mrx)^α + (Muy / Mry)^α ≤ 1.0

        Uses α = 1.15 (log-linear Bresler reciprocal approximation).
        Mrx/Mry = maximum moment capacity at the given Pu from each diagram.
        """

        def get_Mr(diag: list, P_target: float) -> float:
            """Interpolate moment capacity at a given axial load level.

            Walks the sorted (ascending P) diagram and interpolates
            between the two bracketing points.  All M values should
            already be ≥ 0 (absolute capacity).
            """
            sorted_diag = sorted(diag, key=lambda x: x["P"])

            # Clamp if outside range
            if P_target <= sorted_diag[0]["P"]:
                return abs(sorted_diag[0]["M"])
            if P_target >= sorted_diag[-1]["P"]:
                return abs(sorted_diag[-1]["M"])

            for i in range(len(sorted_diag) - 1):
                p1 = sorted_diag[i]["P"]
                p2 = sorted_diag[i + 1]["P"]
                if p1 <= P_target <= p2:
                    m1 = abs(sorted_diag[i]["M"])
                    m2 = abs(sorted_diag[i + 1]["M"])
                    t = (P_target - p1) / (p2 - p1) if p2 != p1 else 0.0
                    return m1 + (m2 - m1) * t
            return 0.0

        Mrx = get_Mr(diagram_x, Pu)
        Mry = get_Mr(diagram_y, Pu)

        if Mrx <= 1e-6 or Mry <= 1e-6:
            # At pure compression/tension, M capacity is near zero.
            # Check if applied moments are also negligible.
            if abs(Mux) < 1.0 and abs(Muy) < 1.0:
                return {"status": "OK", "ratio": 0.0, "Mrx": Mrx, "Mry": Mry}
            return {
                "status": "FAIL - Axial load at/beyond capacity envelope",
                "ratio": 999.0,
                "Mrx": Mrx,
                "Mry": Mry,
            }

        alpha = 1.15  # Bresler exponent (1.15 for rectangular columns)
        ratio = (abs(Mux) / Mrx) ** alpha + (abs(Muy) / Mry) ** alpha

        return {
            "status": "OK" if ratio <= 1.0 else "FAIL - Increase section or rebar",
            "ratio": round(ratio, 4),
            "Mrx": round(Mrx, 2),
            "Mry": round(Mry, 2),
        }

    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    def auto_resize(
        Pu: float, Mux: float, Muy: float,
        fc: float, fy: float,
        b_init: float = 300.0, rho_target: float = 0.02,
        max_iter: int = 20, step_mm: float = 50.0,
    ) -> dict:
        """Auto-iterate column size until biaxial P-M check passes.

        Starts from b_init (square) and grows in step_mm increments.
        Returns the first section that passes with the selected rho.
        """
        b = b_init
        for iteration in range(1, max_iter + 1):
            h = b  # square column
            As_total = rho_target * b * h
            As_per_face = As_total / 2.0
            cover = 50.0
            layers = [
                {"depth": cover, "As": As_per_face},
                {"depth": h - cover, "As": As_per_face},
            ]
            diag = ColumnDesign.generate_interaction_diagram(b, h, fc, fy, layers)
            check = ColumnDesign.check_biaxial_capacity(
                Pu, Mux, Muy, diag["points"], diag["points"]
            )
            if check["status"].startswith("OK"):
                return {
                    "b_mm": b, "h_mm": h,
                    "As_total_mm2": As_total,
                    "rho": rho_target,
                    "iterations": iteration,
                    "biaxial_ratio": check["ratio"],
                    "status": "OK",
                }
            b += step_mm

        return {
            "b_mm": b, "h_mm": b,
            "As_total_mm2": rho_target * b * b,
            "rho": rho_target,
            "iterations": max_iter,
            "biaxial_ratio": check["ratio"],
            "status": "FAIL - Could not converge within max iterations",
        }

    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    def design_shear(
        Vu: float, b: float, d: float, fc: float, fy: float,
        av: float, s: float,
    ) -> dict:
        """Shear design per ACI 318.  Vc = 0.17√fc·b·d."""
        phi = 0.75
        Vc = 0.17 * math.sqrt(fc) * b * d / 1000  # kN
        Vs = (av * fy * d / s) / 1000 if s > 0 else 0
        Vn = Vc + Vs
        status = "OK" if Vu < phi * Vn else "Inadequate Shear Capacity"
        return {"Vc": Vc, "Vs": Vs, "phiVn": phi * Vn, "status": status}

    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    def design_torsion(
        Tu: float, Vu: float, b: float, h: float, fc: float, fy: float,
        at: float, s: float, area_long: float,
    ) -> dict:
        """Torsion design per ACI 318."""
        phi = 0.75
        Acp = b * h
        Pcp = 2 * (b + h)
        T_th = 0.083 * math.sqrt(fc) * (Acp**2 / Pcp) / 1e6  # kN-m

        status = "OK"
        if Tu > phi * T_th:
            if (at * fy * 2 * b * h / s) / 1e6 < Tu:
                status = "Inadequate Torsional Rebar"

        return {"T_threshold": T_th, "status": status}
