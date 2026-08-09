# pyre-ignore-all-errors
import math

# Mathematical boundary guard (plan.md §Defensive Engineering)
EPSILON = 1e-9

class ServiceabilityChecks:
    """Serviceability limit states for Reinforced Concrete."""
    
    @staticmethod
    def check_deflection(M_a: float, M_cr: float, I_g: float, I_cr: float, delta_elastic: float, duration_months: int = 60, rho_prime: float = 0.0) -> dict:
        """
        Calculates long-term deflection using Branson's effective moment of inertia (Ie).
        M_a: Maximum service moment
        M_cr: Cracking moment
        I_g: Gross moment of inertia
        I_cr: Cracked moment of inertia
        delta_elastic: Immediate elastic deflection from FEA
        rho_prime: Compression reinforcement ratio
        """
        # 1. Effective Moment of Inertia (Branson's Formula)
        if M_a <= M_cr:
            I_e = I_g
        else:
            ratio = (M_cr / M_a) ** 3
            I_e = ratio * I_g + (1 - ratio) * I_cr
            I_e = min(I_e, I_g) # Ie cannot exceed Ig
            
        # 2. Modify elastic deflection by ratio of Ig/Ie (since FEA usually uses Ig or a scalar modifier)
        delta_immediate = delta_elastic * (I_g / I_e)
        
        # 3. Long-term multiplier lambda_delta (ACI)
        time_factor = 2.0 # for 5 years or more
        lambda_delta = time_factor / (1 + 50 * rho_prime)
        
        delta_long_term = delta_immediate * (1 + lambda_delta)
        
        return {
            "I_effective_mm4": I_e,
            "delta_immediate_mm": delta_immediate,
            "delta_long_term_mm": delta_long_term,
            "lambda_multiplier": lambda_delta
        }
        
    @staticmethod
    def check_crack_width(fs: float, dc: float, s: float) -> dict:
        """
        ACI 24.3 Simplified crack control constraint.
        Checks maximum spacing of reinforcement (s) to control flexural cracking.
        fs: Calculated stress in reinforcement at service loads (MPa), often approximated as 2/3 * fy
        dc: Distance from extreme tension fiber to centroid of closest bar (mm)
        s: Actual spacing of bars (mm)
        """
        # ACI 318-19 Equation 24.3.2
        # Max spacing s <= 380 * (280 / fs) - 2.5 * cc
        # But not greater than 300 * (280 / fs)
        
        cc = dc - 10 # approximate clear cover from dc
        
        s_max_1 = 380.0 * (280.0 / max(fs, EPSILON)) - 2.5 * cc
        s_max_2 = 300.0 * (280.0 / max(fs, EPSILON))
        
        s_limit = min(s_max_1, s_max_2)
        
        status = "Pass" if s <= s_limit else "Fail"
        
        return {
            "status": status,
            "s_actual_mm": s,
            "s_allowable_mm": s_limit
        }
        
    @staticmethod
    def check_story_drift(delta_x: float, h_x: float, Cd: float, Ie: float, drift_limit_ratio: float = 0.020) -> dict:
        """
        Seismic Story Drift validation per BNBC / ASCE 7.
        delta_x: Elastic story drift from FEA (mm)
        h_x: Story height (mm)
        Cd: Deflection amplification factor
        Ie: Importance factor
        drift_limit_ratio: Allowable ratio, typically 0.020 or 0.025 depending on occupancy
        """
        # Inelastic drift = delta_elastic * Cd / Ie
        delta_inelastic = delta_x * Cd / Ie
        
        drift_ratio = delta_inelastic / max(h_x, EPSILON)
        
        status = "Pass" if drift_ratio <= drift_limit_ratio else "Fail"
        
        return {
            "status": status,
            "inelastic_drift_mm": delta_inelastic,
            "drift_ratio": drift_ratio,
            "drift_limit": drift_limit_ratio
        }
        
    @staticmethod
    def check_floor_vibration(L: float, E: float, I: float, mass_per_length: float) -> dict:
        """
        Checks fundamental frequency of a floor beam for human comfort.
        L in m, E in Pa, I in m^4, mass per length in kg/m.
        Target fn > 4 Hz for normal residential/office floors.
        """
        # fn = (pi / (2 * L^2)) * sqrt(EI / m)
        try:
            fn = (math.pi / (2 * L**2)) * math.sqrt((E * I) / mass_per_length)
        except ZeroDivisionError:
            fn = 0.0
            
        status = "Pass" if fn >= 4.0 else "Fail"
        
        return {
            "status": status,
            "fundamental_frequency_Hz": fn,
            "target_Hz": 4.0
        }
