import sys
import os
import math

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.design.liquid_tank import LiquidTankDesign

def run_problem(id, title, func, **kwargs):
    print(f"\n--- Problem {id}: {title} ---")
    try:
        res = func(**kwargs)
        print(f"Outcome: {res}")
        return res
    except Exception as e:
        print(f"ERROR: {e}")
        return None

print("==================================================")
print("INTENSIVE TEST SUITE - SET 10 (PROBLEMS 46-50)")
print("==================================================")

# Problem 46: Hydrostatic Pressure at 5m depth
run_problem(46, "Hydrostatic Pressure (5m depth)", LiquidTankDesign.calculate_hydrostatic_pressure, 
            h=5.0)

# Problem 47: Buoyancy Stability
# Structure weight 5000kN, Displaced volume 400m3
run_problem(47, "Buoyancy Stability check", LiquidTankDesign.calculate_buoyancy_factor, 
            W_structure=5000.0, V_displaced=400.0)

# Problem 48: Circular Tank Hoop Tension
# R=15m, depth=6m, gamma=10
run_problem(48, "Circular Tank Hoop Tension (R=15, H=6)", LiquidTankDesign.design_circular_tank_wall, 
            radius=15.0, h=6.0, gamma_l=10.0, fy=420.0)

# Problem 49: Buoyancy Failure
run_problem(49, "Buoyancy Failure (Uplift > Weight)", LiquidTankDesign.calculate_buoyancy_factor, 
            W_structure=3000.0, V_displaced=500.0)

# Problem 50: Tank Flexure with S-factor
# Mu=100kNm, b=1000, d=350, fc=25, fy=420
run_problem(50, "Tank Flexure (S=1.3 factor)", LiquidTankDesign.design_tank_flexure, 
            Mu=100.0, b=1000.0, d=350.0, fc=25.0, fy=420.0)
