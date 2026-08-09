# pyre-ignore-all-errors
import math
from backend.api.schemas.design_standards import DomeInput, DomeForces, DomeResult

class DomeDesign:
    """Thin-shell dome design (spherical cap)."""
    
    @staticmethod
    def calculate_membrane_forces(inputs: DomeInput, forces: DomeForces) -> DomeResult:
        """
        Calculates Meridional (N_phi) and Hoop (N_theta) forces for a spherical dome.
        Forces in kN/m.
        """
        w = forces.DL + forces.LL
        theta = math.radians(inputs.theta_edge_deg)
        radius = inputs.radius
        
        # Meridional thrust at the base
        # N_phi = R * w / (1 + cos_theta)
        N_phi = radius * w / (1.0 + math.cos(theta))
        
        # Hoop force at the base
        # N_theta = R * w * (cos_theta - 1 / (1 + cos_theta))
        N_theta = radius * w * (math.cos(theta) - 1.0 / (1.0 + math.cos(theta)))
        
        # Check compression stress
        fc_max = N_phi / inputs.thickness # MPa
        
        # Design Ring Beam tension T = N_phi * cos(theta) * radius * sin(theta)
        ring_tension = N_phi * math.cos(theta) * radius * math.sin(theta)
        As_ring = ring_tension * 1000.0 / (0.87 * 420.0) # 420MPa yield
        
        return DomeResult(
            meridional_force_N_phi_kN_m=float(N_phi),
            hoop_force_N_theta_kN_m=float(N_theta),
            ring_beam_tension_kN=float(ring_tension),
            As_ring_beam_mm2=float(As_ring)
        )
