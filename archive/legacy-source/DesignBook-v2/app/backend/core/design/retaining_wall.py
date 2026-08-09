import math
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class RetainingWallInput(BaseModel):
    height_m: float
    soil_gamma: float = 18.0 # kN/m3
    soil_phi: float = 30.0   # degrees
    surcharge_kpa: float = 0.0
    water_table_depth_m: Optional[float] = None

class RetainingWallDesign:
    """Design module for RC Retaining Walls and Basement Walls."""
    
    @staticmethod
    def calculate_lateral_pressures(inp: RetainingWallInput) -> List[Dict[str, float]]:
        """
        Calculates lateral pressure distribution (Rankine Active).
        Returns a list of pressures at 1m intervals.
        """
        phi_rad = math.radians(inp.soil_phi)
        ka = (1 - math.sin(phi_rad)) / (1 + math.sin(phi_rad))
        
        pressures = []
        for z in range(int(inp.height_m) + 1):
            depth = float(z)
            # Soil pressure
            p_soil = ka * inp.soil_gamma * depth
            # Surcharge pressure
            p_surcharge = ka * inp.surcharge_kpa
            # Water pressure
            p_water = 0.0
            if inp.water_table_depth_m is not None and depth > inp.water_table_depth_m:
                p_water = 9.81 * (depth - inp.water_table_depth_m)
                # Note: Submerged soil gamma should technically be used, 
                # but for simplicity we'll use bulk gamma here.
                
            total_p = p_soil + p_surcharge + p_water
            pressures.append({"depth": depth, "pressure_kpa": total_p})
            
        return pressures
