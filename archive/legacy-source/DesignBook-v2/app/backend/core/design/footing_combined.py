import math

class CombinedFootingDesign:
    """Combined pad footing design for 2 closely spaced columns."""
    
    @staticmethod
    def design(P1: float, P2: float, c_c_dist: float, q_allow: float, fc: float, fy: float) -> dict:
        """
        Determine footprint to match resultant force with centroid of footing area.
        """
        R = P1 + P2
        # Position of resultant from P1
        x_bar = (P2 * c_c_dist) / R
        
        # Length of footing L so that centroid is at x_bar
        # assume column 1 is at edge: distance from edge to P1 = c1/2
        c1 = 0.4
        L = 2 * (x_bar + c1/2)
        
        B = R / (L * q_allow)
        
        # Internal forces: treat as inverted beam loaded by soil pressure
        qu = (R * 1.4) / L
        # Max negative moment between columns
        Mu_neg = qu * (c_c_dist)**2 / 8.0 # Approx
        
        return {
            "L_m": L,
            "B_m": B,
            "qu_kPa": qu,
            "Mu_top_kNm": Mu_neg
        }
