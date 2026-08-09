import sys
import os
import math
import numpy as np

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.design.qto import QuantityTakeoff

def run_problem(id, title, func, **kwargs):
    print(f"\n--- Problem {id}: {title} ---")
    try:
        res = func(**kwargs)
        print(f"Outcome: {res}")
        return res
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

print("==================================================")
print("INTENSIVE TEST SUITE - SET 19 (PROBLEMS 91-95)")
print("==================================================")

# Problem 91: Beam Concrete Volume
def problem_91():
    # Beam 300x500mm, length 6m
    vol = QuantityTakeoff.calculate_concrete_volume(0.3, 0.5, 6.0)
    # 0.3 * 0.5 * 6 = 0.9 m3
    return {"volume_m3": vol}

run_problem(91, "Beam Concrete Quantity", problem_91)

# Problem 92: rebar Weight
def problem_92():
    # 4-20mm bars (Area = 4 * 314 = 1256 mm2), length 6m
    weight = QuantityTakeoff.calculate_rebar_weight(1256.0, 6.0)
    # 1256/1e6 * 6 * 7850 = 59.16 kg
    return {"rebar_kg": weight}

run_problem(92, "Rebar Weight Calculation", problem_92)

# Problem 94: Formwork Area
def problem_94():
    # Beam 300x500mm, length 6m
    area = QuantityTakeoff.calculate_formwork_area(0.3, 0.5, 6.0, "beam")
    # (0.3 + 2*0.5) * 6 = 1.3 * 6 = 7.8 m2
    return {"formwork_m2": area}

run_problem(94, "Beam Formwork Quantity", problem_94)

# Problem 95: Cost Estimate
def problem_95():
    res = QuantityTakeoff.estimate_cost(concrete_m3=100.0, rebar_kg=12000.0, formwork_m2=500.0)
    return res

run_problem(95, "Total Cost Estimation", problem_95)
