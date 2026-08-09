import math
from typing import Dict, Any

class SoilMechanics:
    """Soil reaction and earth pressure calculations."""
    
    @staticmethod
    def calculate_bearing_capacity(c: float, q_overburden: float, gamma: float, B: float, N_c: float, N_q: float, N_gamma: float) -> float:
        """Terzaghi's bearing capacity equation."""
        q_ult = (c * N_c) + (q_overburden * N_q) + (0.5 * gamma * B * N_gamma)
        return q_ult
        
    @staticmethod
    def calculate_winkler_spring_stiffness(q_allowable: float, factor_of_safety: float = 3.0, expected_settlement_m: float = 0.025) -> float:
        """
        Calculates modulus of subgrade reaction (Winkler spring K) based on allowable bearing pressure.
        Bowles' equation: Ks = 40 * F.S. * q_allowable (for settlement of 25mm)
        Returns Ks in kN/m^3.
        """
        q_ult = q_allowable * factor_of_safety
        # If settlement is not 25mm, adjust linearly
        k_s = q_ult / expected_settlement_m
        return k_s
        
    @staticmethod
    def calculate_active_earth_pressure_coefficient(phi_degrees: float, beta_degrees: float = 0) -> float:
        """Rankine active earth pressure coefficient Ka."""
        phi_rad = math.radians(phi_degrees)
        beta_rad = math.radians(beta_degrees)
        
        if beta_degrees == 0:
            return math.tan(math.radians(45 - phi_degrees/2)) ** 2
            
        # Sloping backfill
        cos_beta = math.cos(beta_rad)
        sqrt_term = math.sqrt(math.cos(beta_rad)**2 - math.cos(phi_rad)**2)
        Ka = cos_beta * (cos_beta - sqrt_term) / (cos_beta + sqrt_term)
        return Ka

    @staticmethod
    def calculate_at_rest_earth_pressure_coefficient(phi_degrees: float) -> float:
        """Jaky's empirical equation for at-rest earth pressure Ko."""
        return 1 - math.sin(math.radians(phi_degrees))
