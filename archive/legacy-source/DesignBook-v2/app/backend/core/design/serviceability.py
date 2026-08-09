import math

class ServiceabilityDesign:
    """Serviceability limit state checks (Deflection, Cracking, Vibration)."""
    
    @staticmethod
    def calculate_effective_inertia(Mcr: float, Ma: float, Ig: float, Icr: float) -> float:
        """
        Calculates Branson's Effective Moment of Inertia (Ie).
        Mcr: Cracking moment, Ma: Maximum service moment, Ig: Gross I, Icr: Cracked I.
        """
        if Ma <= Mcr:
            return Ig
        
        ratio = Mcr / Ma
        Ie = (ratio**3) * Ig + (1 - ratio**3) * Icr
        return min(Ie, Ig)

    @staticmethod
    def calculate_long_term_deflection_multiplier(xi: float, rho_prime: float) -> float:
        """
        Calculates lambda_delta = xi / (1 + 50 * rho_prime)
        xi: Time-dependent factor (2.0 for 5+ years, 1.4 for 12 months, etc.)
        """
        return xi / (1 + 50 * rho_prime)

    @staticmethod
    def check_crack_width(fs: float, dc: float, A: float) -> float:
        """
        Gergely-Lutz equation for crack width w (mm).
        fs: steel stress (MPa), dc: cover to center of bar (mm), A: effective tension area per bar.
        w = 1.1e-5 * beta * fs * (dc * A)^(1/3)
        """
        beta = 1.2 # common for beams
        w = 1.1e-6 * beta * fs * math.pow(dc * A, 1/3) # result in mm
        return w

    @staticmethod
    def calculate_beam_frequency(E: float, I: float, L: float, mass_per_meter: float) -> float:
        """
        Fundamental frequency of a simply supported beam (Hz).
        fn = (pi/2) * sqrt(EI / mL^4)
        """
        # units must be consistent (SI: Pascal, m^4, m, kg/m)
        fn = (math.pi / 2) * math.sqrt((E * I) / (mass_per_meter * L**4))
        return fn
