# pyre-ignore-all-errors
import math
from typing import Dict, Any
from backend.api.schemas.design_standards import CFSWidthInput, CFSColumnInput

class CFSDesign:
    """Design routines for Cold-Formed Steel (AISI/BNBC)."""
    
    @staticmethod
    def calculate_effective_width(inputs: CFSWidthInput) -> float:
        """
        Calculates effective width due to local buckling (Simplified AISI).
        w: flat width, t: thickness, f: stress in element.
        """
        w = inputs.w
        t = inputs.t
        f = inputs.f
        E = inputs.E
        
        if f <= 0: return w
        
        # Buckling coefficient k = 4.0 for stiffened element
        k = 4.0
        # Slenderness factor lambda = (w/t) / sqrt(E/f) * sqrt(12*(1-v^2)/(pi^2 * k))
        # Simplified: lambda = (w/t) * sqrt(f/E) / 0.95
        lam = (w / t) * math.sqrt(f / E) / 0.95
        
        if lam <= 0.673:
            return w
        
        rho = (1.0 - 0.22 / lam) / lam
        return w * rho

    @staticmethod
    def design_column_capacity(inputs: CFSColumnInput) -> float:
        """Calculates nominal axial capacity (Flexural buckling)."""
        L = inputs.L
        r = inputs.r
        E = inputs.E
        fy = inputs.fy
        A = inputs.A
        
        Fe = (math.pi**2 * E) / ((L / r)**2)
        lam_c = math.sqrt(fy / Fe)
        
        if lam_c <= 1.5:
            Fn = (0.658**(lam_c**2)) * fy
        else:
            Fn = (0.877 / (lam_c**2)) * fy
            
        return Fn * A / 1000.0 # kN
