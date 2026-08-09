# pyre-ignore-all-errors
import math
from typing import Dict, List, Tuple, Optional, Any, cast

class BarCatalog:
    """Standard Metric Rebar Catalog for ACI / BNBC referencing."""
    BARS = {
        8:  {"area": 50.3,   "dia": 8,   "name": "T8"},
        10: {"area": 78.5,   "dia": 10,  "name": "T10"},
        12: {"area": 113.1,  "dia": 12,  "name": "T12"},
        16: {"area": 201.1,  "dia": 16,  "name": "T16"},
        20: {"area": 314.2,  "dia": 20,  "name": "T20"},
        22: {"area": 380.1,  "dia": 22,  "name": "T22"},
        25: {"area": 490.9,  "dia": 25,  "name": "T25"},
        28: {"area": 615.8,  "dia": 28,  "name": "T28"},
        32: {"area": 804.2,  "dia": 32,  "name": "T32"}
    }
    
    @classmethod
    def get_area(cls, dia: int) -> float:
        return float(cls.BARS.get(dia, {}).get("area", (math.pi * dia**2) / 4))

class DetailingEngine:
    """Methods isolating raw A_s and A_v translation into constructible bar allocations."""
    
    @staticmethod
    def select_flexural_bars(
        As_req: float, 
        b_mm: float, 
        cover_mm: float = 40.0, 
        stirrup_dia: int = 10,
        min_bars: int = 2,
        prefer_dia: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Finds the optimal symmetric bar arrangement satisfying As_req within beam width b."""
        if As_req <= 0:
            return cast(Dict[str, Any], {"arrangement": "None", "As_prov": 0, "bars": 0, "dia": 0, "bars_fit": True})
            
        if prefer_dia is None:
            prefer_dia = [12, 16, 20, 25, 32]
            
        best_fit = None
        min_waste = float('inf')
        
        for dia in prefer_dia:
            bar_area = BarCatalog.get_area(dia)
            num_bars = max(min_bars, math.ceil(As_req / bar_area))
            As_prov = num_bars * bar_area
            
            waste = As_prov - As_req
            
            # Check if they fit in one layer
            # Minimum clear spacing is max(25mm, db, (4/3)*d_agg) -> assume 25mm or db
            clear_spacing = max(25.0, float(dia))
            core_width = b_mm - 2 * cover_mm - 2 * stirrup_dia
            
            # required width = n*db + (n-1)*clear_spacing
            req_width = num_bars * dia + max(0, num_bars - 1) * clear_spacing
            
            fits_in_one_layer = req_width <= core_width
            
            num_layers = 1
            if not fits_in_one_layer:
                # If it doesn't fit, calculate how many layers needed (assuming pairs can stack)
                bars_per_layer = math.floor((core_width + clear_spacing) / (dia + clear_spacing))
                if bars_per_layer < 2:
                    bars_per_layer = 1 # physically impossible to fit even 2 bars
                num_layers = math.ceil(num_bars / bars_per_layer)
            
            if waste < min_waste and num_layers <= 2:  # Prefer max 2 layers
                min_waste = waste
                best_fit = {
                    "arrangement": f"{num_bars}-{BarCatalog.BARS[dia]['name']}", 
                    "As_prov": float(f"{float(As_prov):.1f}"),
                    "bars": num_bars,
                    "dia": dia,
                    "layers": num_layers,
                    "bars_fit": num_layers <= 2
                }
                
        if not best_fit:
            # Fallback to absolute minimum waste regardless of layers if geometry is terrible
            best_fit = {"arrangement": "Requires resizing - too many layers", "As_prov": As_req, "bars": 0, "dia": 0, "layers": 3, "bars_fit": False}
            
        return cast(Dict[str, Any], best_fit)

    @staticmethod
    def select_shear_spacing(
        Av_over_s_req: float, 
        d_mm: float, 
        stirrup_legs: int = 2, 
        preferred_dia: int = 10,
        max_spacing_rule: Optional[float] = None
    ) -> Dict[str, Any]:
        """Translates Av/s (mm^2/mm) into a concrete stirrup spacing e.g., T10@150 c/c."""
        dia = preferred_dia
        Av_total = stirrup_legs * BarCatalog.get_area(dia)
        
        # Determine maximum code spacing
        s_max = min(d_mm / 2, 600.0)
        if max_spacing_rule:
            s_max = min(s_max, max_spacing_rule)
            
        if Av_over_s_req <= 0:
            return cast(Dict[str, Any], {
                "arrangement": f"{stirrup_legs}L-{BarCatalog.BARS[dia]['name']} @ {int(s_max)} c/c",
                "spacing": int(s_max),
                "dia": dia
            })
            
        # Required spacing
        s_req = min(s_max, Av_total / Av_over_s_req)
        
        # Round down to nearest 25mm for constructability
        s_constructible = max(50.0, math.floor(s_req / 25.0) * 25.0)
        
        return cast(Dict[str, Any], {
            "arrangement": f"{stirrup_legs}L-{BarCatalog.BARS[dia]['name']} @ {int(s_constructible)} c/c",
            "spacing": int(s_constructible),
            "dia": dia
        })

    @staticmethod
    def detail_column(
        b: float, h: float, As_req: float, 
        pu_kn: float = 0, fc: float = 30
    ) -> Dict[str, Any]:
        """Details column longitudinal and transverse reinforcement."""
        Ag = b * h
        rho_req = As_req / Ag
        
        # 1% to 8% gross limits
        rho_min = 0.010
        rho_target = max(rho_req, rho_min)
        if rho_target > 0.08:
            return cast(Dict[str, Any], {"status": "FAIL: Requires > 8% steel"})
            
        As_target = rho_target * Ag
        
        # Columns require bars on all faces. Minimum 4 bars for rectangular.
        # Pick bar size to satisfy As_target with even number of bars >= 4.
        best_dia = 16
        best_num = 4
        min_waste = float('inf')
        
        for dia in [16, 20, 25, 28, 32]:
            area = BarCatalog.get_area(dia)
            n_bars = max(4, math.ceil(As_target / area))
            # ensure even number of bars for symmetry
            if n_bars % 2 != 0:
                n_bars += 1
                
            prov_as = n_bars * area
            waste = prov_as - As_target
            
            # Check clear spacing between longitudinal bars
            # simplify: assume bars placed equally on 2 faces for spacing check
            bars_per_face = (n_bars - 4) // 2 + 2
            clear_s = (b - 80 - 20) / (bars_per_face - 1) if bars_per_face > 1 else 999
            
            if clear_s >= 40 and waste < min_waste:
                min_waste = waste
                best_dia = dia
                best_num = n_bars

        # Ties
        tie_dia = 10 if best_dia <= 32 else 12
        s_max = min(float(16 * int(best_dia)), float(48 * tie_dia), float(b), float(h))
        s_max_constructible = math.floor(s_max / 25.0) * 25.0

        return cast(Dict[str, Any], {
            "longitudinal": f"{best_num}-{BarCatalog.BARS[best_dia]['name']}",
            "transverse": f"T{tie_dia} @ {int(s_max_constructible)} c/c",
            "As_prov": float(f"{float(best_num) * BarCatalog.get_area(best_dia):.1f}"),
            "rho_prov": float(f"{float(best_num) * BarCatalog.get_area(best_dia) / Ag * 100:.2f}")
        })

    @staticmethod
    def detail_slab(
        thickness: float,
        As_main: float,
        As_temp: float,
        main_dia: int = 10,
        temp_dia: int = 10
    ) -> Dict[str, Any]:
        """Generates mm spacing for required slab areas."""
        main_a = BarCatalog.get_area(main_dia)
        temp_a = BarCatalog.get_area(temp_dia)
        
        s_main_req = float((main_a * 1000) / As_main) if As_main > 0 else 300.0
        s_main_max = min(float(2 * thickness), 450.0)
        s_main = min(s_main_req, s_main_max)
        s_main = max(75.0, float(math.floor(s_main / 25.0) * 25.0))
        
        s_temp_req = float((temp_a * 1000) / As_temp) if As_temp > 0 else 450.0
        s_temp_max = min(float(5 * thickness), 450.0)
        s_temp = min(s_temp_req, s_temp_max)
        s_temp = max(75.0, float(math.floor(s_temp / 25.0) * 25.0))
        
        return cast(Dict[str, Any], {
            "main_reinforcement": f"T{main_dia} @ {int(s_main)} c/c",
            "temp_reinforcement": f"T{temp_dia} @ {int(s_temp)} c/c"
        })
