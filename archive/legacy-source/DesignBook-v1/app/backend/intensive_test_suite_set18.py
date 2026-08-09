import sys
import os
import math
import numpy as np

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.loads.seismic import calculate_seismic_loads, SeismicInput, SeismicResult

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
print("INTENSIVE TEST SUITE - SET 18 (PROBLEMS 86-90)")
print("==================================================")

# Problem 86: Story Drift Calculation
def problem_86():
    elevs = [3.0, 6.0, 9.0]
    disps = [0.005, 0.012, 0.020] # Elastic disps in m
    drifts = SeismicResult.calculate_story_drifts(disps, elevs, Cd=5.5)
    # Story 1: 5.5 * 0.005 / 3 = 0.0091
    # Story 2: 5.5 * (0.012 - 0.005) / 3 = 0.0128
    return drifts

run_problem(86, "Story Drift (Inelastic)", problem_86)

# Problem 88: Stability Coefficient Theta
def problem_88():
    # P=1000kN, delta_elastic=0.01m, V=100kN, h=3m, Cd=5.5
    delta_inelastic = 5.5 * 0.01
    theta = SeismicResult.calculate_stability_coefficient(1000.0, delta_inelastic, 100.0, 3.0, Cd=5.5)
    # theta = (1000 * 0.055) / (100 * 3 * 5.5) = 55 / 1650 = 0.033
    return {"theta": theta, "pdelta_required": theta > 0.1}

run_problem(88, "Stability Coefficient Calculation", problem_88)

# Problem 89: 5-Story ESFM Distribution
def problem_89():
    weights = [1000.0] * 5
    elevs = [3.0 * (i+1) for i in range(5)]
    inp = SeismicInput("II", "SC", "residential", "IMRF", 15.0, weights, elevs)
    res = calculate_seismic_loads(inp)
    return {"base_shear": res.base_shear_kn, "top_force": res.story_forces[-1].force_kn}

run_problem(89, "5-Story Seismic Force Distribution", problem_89)
