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
        
    @staticmethod
    def generate_foundation_springs(
        Ks_kpa_m: float, 
        length_m: float, 
        width_m: float,
        depth_m: float = 0.0,
        soil_poisson: float = 0.3
    ) -> Dict[str, float]:
        """
        Generates 6-DOF elastic spring constants for a shallow foundation (e.g., footing/raft).
        Based on Gazetas (1991) formulas for dynamic stiffness, adapted for static springs.
        
        Returns a dict of spring stiffnesses [Kx, Ky, Kz, KRx, KRy, KRz] in kN/m and kN-m/rad.
        """
        # Vertical spring (Z-direction)
        area = length_m * width_m
        Kz = Ks_kpa_m * area
        
        # Lateral springs (X and Y directions) - approx 0.5 to 1.0 of Kz based on friction/embedment
        # For a surface footing without passive pressure, shear modulus G controls
        # Simplified ratio: Kx = Ky ~= 0.8 Kz
        embedment_factor = 1.0 + 0.2 * (depth_m / min(length_m, width_m))
        Kx = 0.8 * Kz * embedment_factor
        Ky = 0.8 * Kz * embedment_factor
        
        # Rotational springs (Rocking)
        # KRx = Kz * I_x, KRy = Kz * I_y
        Ix = (length_m * width_m**3) / 12.0
        Iy = (width_m * length_m**3) / 12.0
        
        KRx = Ks_kpa_m * Ix
        KRy = Ks_kpa_m * Iy
        
        # Torsional spring (Z-axis rotation)
        Jz = Ix + Iy
        KRz = 0.5 * Ks_kpa_m * Jz # approximate torsional stiffness
        
        return {
            "Kx": Kx, "Ky": Ky, "Kz": Kz,
            "KRx": KRx, "KRy": KRy, "KRz": KRz
        }

