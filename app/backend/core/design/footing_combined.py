# pyre-ignore-all-errors
import math
from backend.api.schemas.design_standards import CombinedFootingInput, CombinedFootingForces, CombinedFootingResult

class CombinedFootingDesign:
    """Combined pad footing design for 2 closely spaced columns."""
    
    @staticmethod
    def design(inputs: CombinedFootingInput, forces: CombinedFootingForces) -> CombinedFootingResult:
        """
        Determine footprint to match resultant force with centroid of footing area.
        """
        P1 = forces.P1
        P2 = forces.P2
        R = P1 + P2
        
        # Prevent division by zero
        if R <= 0:
            return CombinedFootingResult(L_m=0.0, B_m=0.0, qu_kPa=0.0, Mu_top_kNm=0.0)
            
        # Position of resultant from P1
        x_bar = (P2 * inputs.c_c_dist) / R
        
        # Length of footing L so that centroid is at x_bar
        # assume column 1 is at edge: distance from edge to P1 = c1/2
        c1 = 0.4
        L = 2 * (x_bar + c1/2)
        
        B = R / (L * inputs.q_allow) if (L * inputs.q_allow) > 0 else 0
        
        # Internal forces: treat as inverted beam loaded by soil pressure
        qu = (R * 1.4) / L if L > 0 else 0
        # Max negative moment between columns
        Mu_neg = qu * (inputs.c_c_dist)**2 / 8.0 # Approx
        
        return CombinedFootingResult(
            L_m=float(L),
            B_m=float(B),
            qu_kPa=float(qu),
            Mu_top_kNm=float(Mu_neg)
        )
