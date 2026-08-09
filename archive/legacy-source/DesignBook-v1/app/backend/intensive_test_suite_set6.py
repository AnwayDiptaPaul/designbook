import sys
import os
import math

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.design.staircase import StaircaseDesign
from core.design.dome import DomeDesign

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
print("INTENSIVE TEST SUITE - SET 6 (PROBLEMS 26-30)")
print("==================================================")

# Problem 26: Straight Staircase with 5m span
run_problem(26, "Staircase High Span (5m)", StaircaseDesign.design, 
            going=5.0, rise=150.0, tread=250.0, width=1.2, LL=5.0, fc=25.0, fy=420.0)

# Problem 27: Dog-legged Staircase with heavy LL (10 kPa)
run_problem(27, "Staircase Heavy Load (LL=10)", StaircaseDesign.design, 
            going=3.0, rise=150.0, tread=250.0, width=1.5, LL=10.0, fc=30.0, fy=420.0)

# Problem 28: Concrete Dome (R=10m, thickness=100mm, theta=45 deg)
run_problem(28, "Concrete Dome Membrane Force (R=10, 45 deg)", DomeDesign.calculate_membrane_forces, 
            radius=10.0, thickness=0.1, DL=4.0, LL=2.0, theta_edge_deg=45.0)

# Problem 29: Dome at 90 deg (Hemisphere) - Maximum Meridional Thrust
run_problem(29, "Hemispherical Dome (90 deg)", DomeDesign.calculate_membrane_forces, 
            radius=8.0, thickness=0.1, DL=3.0, LL=1.0, theta_edge_deg=90.0)

# Problem 30: Very Flat Dome (theta=20 deg) - High Hoop Tension
run_problem(30, "Shallow Dome (20 deg)", DomeDesign.calculate_membrane_forces, 
            radius=15.0, thickness=0.1, DL=5.0, LL=2.0, theta_edge_deg=20.0)
