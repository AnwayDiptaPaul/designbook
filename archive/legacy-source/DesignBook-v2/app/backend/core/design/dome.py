import math

class DomeDesign:
    """Thin-shell dome design (spherical cap)."""
    
    @staticmethod
    def calculate_membrane_forces(radius: float, thickness: float, DL: float, LL: float, theta_edge_deg: float) -> dict:
        """
        Calculates Meridional (N_phi) and Hoop (N_theta) forces for a spherical dome.
        Forces in kN/m.
        """
        w = DL + LL
        theta = math.radians(theta_edge_deg)
        
        # Meridional thrust at the base
        # N_phi = R * w / (1 + cos_theta)
        N_phi = radius * w / (1 + math.cos(theta))
        
        # Hoop force at the base
        # N_theta = R * w * (cos_theta - 1 / (1 + cos_theta))
        N_theta = radius * w * (math.cos(theta) - 1.0 / (1.0 + math.cos(theta)))
        
        # Check compression stress
        fc_max = N_phi / (thickness * 1000) # MPa
        
        # Design Ring Beam tension T = N_phi * cos(theta) * radius * sin(theta)
        ring_tension = N_phi * math.cos(theta) * radius * math.sin(theta)
        As_ring = ring_tension * 1000 / (0.87 * 420) # 420MPa yield
        
        return {
            "meridional_force_N_phi_kN_m": N_phi,
            "hoop_force_N_theta_kN_m": N_theta,
            "ring_beam_tension_kN": ring_tension,
            "As_ring_beam_mm2": As_ring
        }
