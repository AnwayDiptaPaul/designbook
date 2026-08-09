# pyre-ignore-all-errors
import math
from typing import List, Dict

class QuantityTakeoff:
    """Calculates concrete volumes, rebar weights, and formwork areas."""
    
    # Standard densities
    CONCRETE_DENSITY_KG_M3 = 2400.0
    STEEL_DENSITY_KG_M3 = 7850.0
    
    @staticmethod
    def calculate_bar_weight(diameter_mm: float, length_m: float) -> float:
        """Weight of a single steel rebar in kg."""
        # W = (D^2 / 162) * L   [empirical formula for kg]
        return (diameter_mm**2 / 162.2) * length_m
        
    @staticmethod
    def beam_takeoff(b_mm: float, h_mm: float, L_m: float, main_bars: List[Dict], stirrups: Dict) -> dict:
        """
        Takeoff for a single beam.
        main_bars: [{"dia": 16, "num": 4, "length": 6.0}, ...]
        stirrups: {"dia": 10, "spacing_mm": 150}
        """
        vol_concrete_m3 = (b_mm / 1000) * (h_mm / 1000) * L_m
        
        # Main steel weight
        weight_main_kg = 0.0
        for bar in main_bars:
            weight_main_kg += QuantityTakeoff.calculate_bar_weight(bar["dia"], bar["length"]) * bar["num"]
            
        # Stirrup weight
        num_stirrups = math.ceil((L_m * 1000) / stirrups["spacing_mm"])
        # Perimeter approx (minus cover 40mm each side)
        stirrup_length_m = 2 * ((b_mm - 80) + (h_mm - 80)) / 1000 + 0.15 # 150mm hook allowance
        weight_stirrup_kg = num_stirrups * QuantityTakeoff.calculate_bar_weight(stirrups["dia"], stirrup_length_m)
        
        # Formwork area (bottom + 2 sides)
        area_formwork_m2 = ((b_mm + 2 * h_mm) / 1000) * L_m
        
        return {
            "concrete_vol_m3": vol_concrete_m3,
            "rebar_weight_kg": weight_main_kg + weight_stirrup_kg,
            "formwork_area_m2": area_formwork_m2,
            "steel_ratio_kg_m3": (weight_main_kg + weight_stirrup_kg) / vol_concrete_m3 if vol_concrete_m3 > 0 else 0
        }
