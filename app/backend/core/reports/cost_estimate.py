# pyre-ignore-all-errors
from typing import Dict, Any


class CostEstimate:
    """Estimates construction cost based on Bangladesh PWD Schedule of Rates 2022/2024."""
    
    # Mock Rates (in BDT)
    RATES = {
        "concrete_m3": 9500.0, # Ready mix 3500 psi
        "rebar_kg": 115.0, # 500W steel
        "formwork_m2": 450.0, # Steel shuttering
        "labor_factor": 1.15, # 15% overhead for labor and pouring
    }
    
    @staticmethod
    def calculate_cost(concrete_vol_m3: float, rebar_weight_kg: float, formwork_area_m2: float):
        """Computes cost breakdown and total."""
        
        cost_concrete = concrete_vol_m3 * CostEstimate.RATES["concrete_m3"]
        cost_rebar = rebar_weight_kg * CostEstimate.RATES["rebar_kg"]
        cost_formwork = formwork_area_m2 * CostEstimate.RATES["formwork_m2"]
        
        subtotal = cost_concrete + cost_rebar + cost_formwork
        total = subtotal * CostEstimate.RATES["labor_factor"]
        
        return {
            "currency": "BDT",
            "breakdown": {
                "concrete": cost_concrete,
                "rebar": cost_rebar,
                "formwork": cost_formwork,
                "labor_and_overhead": total - subtotal
            },
            "subtotal": subtotal,
            "total_estimated_cost": total
        }
