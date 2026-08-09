import math
from typing import Dict, Any, List

class QuantityTakeoff:
    """Quantity Takeoff (QTO) and Cost Estimation per local PWD rates."""
    
    @staticmethod
    def calculate_concrete_volume(B: float, H: float, L: float) -> float:
        """Volume in m3."""
        return B * H * L

    @staticmethod
    def calculate_rebar_weight(area_mm2: float, length_m: float) -> float:
        """Weight in kg. Density = 7850 kg/m3."""
        area_m2 = area_mm2 / 1e6
        return area_m2 * length_m * 7850.0

    @staticmethod
    def calculate_formwork_area(B: float, H: float, L: float, member_type: str ="beam") -> float:
        """Formwork area in m2."""
        if member_type.lower() == "beam":
            # 2 sides + bottom
            return (2 * H + B) * L
        elif member_type.lower() == "column":
            # 4 sides
            return 2 * (B + H) * L
        elif member_type.lower() == "slab":
            # bottom surface
            return B * L
        return 0.0

    @staticmethod
    def estimate_cost(concrete_m3: float, rebar_kg: float, formwork_m2: float) -> Dict[str, Any]:
        """
        Estimates total cost based on sample PWD 2022 rates.
        Concrete (1:1.5:3): 12000 BDT/m3
        Rebar (72.5 grade): 105 BDT/kg
        Formwork: 650 BDT/m2
        """
        rates = {"concrete": 12000.0, "rebar": 105.0, "formwork": 650.0}
        c_cost = concrete_m3 * rates["concrete"]
        r_cost = rebar_kg * rates["rebar"]
        f_cost = formwork_m2 * rates["formwork"]
        total = c_cost + r_cost + f_cost
        
        return {
            "concrete_cost": c_cost,
            "rebar_cost": r_cost,
            "formwork_cost": f_cost,
            "total_estimated_cost": total
        }
