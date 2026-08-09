import sys
import os
import math

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.design.retaining_wall import RetainingWallDesign

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
print("INTENSIVE TEST SUITE - SET 5 (PROBLEMS 21-25)")
print("==================================================")

# Problem 21: Standard Cantilever Wall (4m)
run_problem(21, "Standard Retaining Wall (H=4m)", RetainingWallDesign.check_stability, 
            H=4.0, Tw=0.3, Tb=0.4, Ltoe=1.0, Lheel=2.0, gamma_s=18.0, phi_s=30.0, 
            q_surcharge=10.0, mu=0.5, q_allow=200.0)

# Problem 22: High Surcharge (Overturning check)
run_problem(22, "High Surcharge Wall (qs=50)", RetainingWallDesign.check_stability, 
            H=3.0, Tw=0.25, Tb=0.4, Ltoe=0.5, Lheel=1.0, gamma_s=18.0, phi_s=30.0, 
            q_surcharge=50.0, mu=0.4, q_allow=150.0)

# Problem 23: Low soil friction (Sliding check)
run_problem(23, "Low Friction Soil (phi=20)", RetainingWallDesign.check_stability, 
            H=4.0, Tw=0.3, Tb=0.5, Ltoe=0.8, Lheel=1.5, gamma_s=17.0, phi_s=20.0, 
            q_surcharge=5.0, mu=0.3, q_allow=150.0)

# Problem 24: Tall Wall Stem Design
run_problem(24, "Tall Wall Stem (H=6m) Flexure", RetainingWallDesign.design_stem, 
            H=6.0, Tw=0.5, fc=28.0, fy=420.0, gamma_s=18.0, phi_s=30.0, q_surcharge=10.0)

# Problem 25: Very tall wall (8m) on soft soil
run_problem(25, "Tall Wall (H=8m) Bearing Check", RetainingWallDesign.check_stability, 
            H=8.0, Tw=0.6, Tb=0.8, Ltoe=1.5, Lheel=3.5, gamma_s=19.0, phi_s=30.0, 
            q_surcharge=10.0, mu=0.5, q_allow=150.0)
