import math

class DetailingDesign:
    """Rebar Detailing and Anchorage routines per ACI 318 / BNBC 2020."""
    
    @staticmethod
    def calculate_development_length_tension(db: float, fy: float, fc: float, 
                                             psi_t: float=1.0, psi_e: float=1.0, 
                                             psi_s: float=1.0, lambda_f: float=1.0, 
                                             cb: float=40, Ktr: float=0) -> float:
        """
        Calculates ld (mm) for tension bars.
        db: bar diameter (mm).
        psi_t: casting position, psi_e: epoxy, psi_s: size factor.
        """
        # ACI 318-19 Eq: ld = (3/40 * fy / (lambda * sqrt(fc)) * (psi_t*psi_e*psi_s*psi_g / ((cb+Ktr)/db))) * db
        # Simplified for common cases if (cb+Ktr)/db is not provided:
        confinement = min((cb + Ktr) / db, 2.5) if db > 0 else 2.5
        
        ld = (3/40) * (fy / (lambda_f * math.sqrt(fc))) * (psi_t * psi_e * psi_s / confinement) * db
        return max(ld, 300.0) # ld_min = 300mm

    @staticmethod
    def calculate_hook_development_length(db: float, fy: float, fc: float, 
                                          psi_e: float=1.0, psi_r: float=1.0, 
                                          psi_o: float=1.0, psi_c: float=1.0) -> float:
        """Calculates ldh (mm) for standard hooks in tension."""
        # ldh = (fy * psi_e * psi_r * psi_o * psi_c / (2.1 * lambda * sqrt(fc))) * db^1.5 / ... 
        # ACI 318-19 simplified form:
        ldh = (fy * psi_e * psi_r * psi_o / (2.1 * 1.0 * math.sqrt(fc))) * math.pow(db, 1.5) / 10.0 # Factor adjust
        # More accurately per ACI 318-19 Table 25.4.3.1:
        ldh = (fy * psi_e * psi_r * psi_o / (2.1 * math.sqrt(fc))) * db
        return max(ldh, 8 * db, 150.0)

    @staticmethod
    def calculate_lap_splice_tension(ld: float, splice_class: str="B") -> float:
        """Calculates Tension Lap Splice length."""
        if splice_class.upper() == "A":
            return max(1.0 * ld, 300.0)
        else: # Class B
            return max(1.3 * ld, 300.0)

    @staticmethod
    def check_min_spacing(db: float, s_center: float, aggravate_size: float=20.0, layer_type: str="horizontal") -> str:
        """Checks if clear spacing satisfies ACI 25.2."""
        clear_s = s_center - db
        s_min = max(db, 25.0, (4/3) * aggravate_size)
        if layer_type == "vertical":
            s_min = 25.0
            
        return "OK" if clear_s >= s_min else f"FAIL - Clear spacing {clear_s:.1f} < min {s_min:.1f}"
