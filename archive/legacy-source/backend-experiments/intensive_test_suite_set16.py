import sys
import os
import math
import numpy as np

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.loads.wind import calculate_wind_loads, WindLoadInput, interpolate_kz

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
print("INTENSIVE TEST SUITE - SET 16 (PROBLEMS 76-80)")
print("==================================================")

# Problem 76: Velocity Pressure qz at 30m, Exposure C
def problem_76():
    V = 45.0 # m/s
    Kz = interpolate_kz(30.0, "C")
    # qz = 0.613 * Kz * Kzt * Kd * V^2
    qz = 0.613 * Kz * 1.0 * 0.85 * (V**2)
    return {"Kz_30m": Kz, "qz_pa": qz}

run_problem(76, "Wind Velocity Pressure (Exp C, 30m)", problem_76)

# Problem 77: 10-Story Building Wind Forces
def problem_77():
    elevations = [3.0 * i for i in range(1, 11)] # 3m, 6m... 30m
    heights = [3.0] * 10
    inp = WindLoadInput(
        basic_wind_speed_mps=45.0,
        exposure_category="B",
        building_width_m=20.0,
        building_depth_m=15.0,
        floor_elevations_m=elevations,
        floor_heights_m=heights
    )
    res = calculate_wind_loads(inp)
    return {"base_shear_kn": res.base_shear_kn, "overturning_moment_knm": res.overturning_moment_knm}

run_problem(77, "10-Story Buildng Wind Force Profile", problem_77)

# Problem 78: Windward vs Leeward splitting
def problem_78():
    inp = WindLoadInput(45.0, "C", floor_elevations_m=[10.0], floor_heights_m=[3.0])
    res = calculate_wind_loads(inp)
    prof = res.pressure_profile[0]
    # Ratio should be |0.8 / -0.5| approx 1.6
    ratio = abs(prof["p_windward_pa"] / prof["p_leeward_pa"]) if prof["p_leeward_pa"] != 0 else 0
    return {"ratio_w_l": ratio}

run_problem(78, "Windward/Leeward Pressure Ratio", problem_78)

# Problem 80: Exposure category comparison (B vs D)
def problem_80():
    z = 60.0 # High rise level
    kz_b = interpolate_kz(z, "B")
    kz_d = interpolate_kz(z, "D")
    # Exp D should be much higher than B at high altitude
    return {"Kz_B": kz_b, "Kz_D": kz_d, "ratio_D_B": kz_d / kz_b}

run_problem(80, "Exposure B vs D Comparison at 60m", problem_80)
