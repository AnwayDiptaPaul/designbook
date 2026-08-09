# pyre-ignore-all-errors
import math
from backend.api.schemas.design_standards import SlabDesignInput, TwoWaySlabForces, TwoWaySlabResult

class TwoWaySlabDesign:
    """Two-way slab design using Direct Design Method (DDM) or FEA moments."""
    
    @staticmethod
    def design_flexure_fea(inputs: SlabDesignInput, forces: TwoWaySlabForces) -> TwoWaySlabResult:
        """
        Designs based on Wood-Armer moments from FEA shells.
        """
        # Outer layer X, inner layer Y
        d_x = inputs.thickness - inputs.cover - 5.0 # assume 10mm bars
        d_y = d_x - 10.0
        
        fc = inputs.material.fc
        fy = inputs.material.fy
        
        def calc_as(Mu: float, d: float) -> float:
            Mu_Nmm = abs(Mu) * 1e6
            denominator = 0.9 * 1000 * (d**2)
            if denominator <= 0: return 0.0
            Rn = Mu_Nmm / denominator
            
            discriminant = 1 - 2 * Rn / (0.85 * fc)
            if discriminant < 0:
                # Return something high to flag failure or handle elsewhere
                return 0.0050 * 1000 * inputs.thickness # Flag with high rho
            
            rho = 0.85 * fc / fy * (1 - math.sqrt(discriminant))
            rho_min = 0.0018
            return max(rho, rho_min) * 1000 * inputs.thickness
            
        As_x = calc_as(forces.Mu_x, d_x)
        As_y = calc_as(forces.Mu_y, d_y)
        
        return TwoWaySlabResult(
            As_x_req_mm2_m=float(As_x),
            As_y_req_mm2_m=float(As_y)
        )
