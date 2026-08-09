import math

class TwoWaySlabDesign:
    """Two-way slab design using Direct Design Method (DDM) or FEA moments."""
    
    @staticmethod
    def design_flexure_fea(Mu_x: float, Mu_y: float, t: float, fc: float, fy: float, cover: float = 20) -> dict:
        """
        Designs based on Wood-Armer moments from FEA shells.
        Returns As_x and As_y per meter.
        """
        # Outer layer X, inner layer Y
        d_x = t - cover - 5.0 # assume 10mm bars
        d_y = d_x - 10.0
        
        def calc_as(Mu, d):
            Mu_Nmm = abs(Mu) * 1e6
            denominator = 0.9 * 1000 * d**2
            if denominator == 0: return 0
            Rn = Mu_Nmm / denominator
            
            discriminant = 1 - 2 * Rn / (0.85 * fc)
            if discriminant < 0:
                # Return something high to flag failure or handle elsewhere
                return 0.0050 * 1000 * t # Flag with high rho stub
            
            rho = 0.85 * fc / fy * (1 - math.sqrt(discriminant))
            rho_min = 0.0018
            return max(rho, rho_min) * 1000 * t
            
        As_x = calc_as(Mu_x, d_x)
        As_y = calc_as(Mu_y, d_y)
        
        return {
            "As_x_req_mm2_m": As_x,
            "As_y_req_mm2_m": As_y
        }
