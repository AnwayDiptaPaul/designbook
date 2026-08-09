import sys
import os
import math

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.design.shear_wall import ShearWallDesign
from core.design.footing_isolated import IsolatedFootingDesign

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
print("INTENSIVE TEST SUITE - SET 3 (PROBLEMS 11-15)")
print("==================================================")

# Problem 11: Shear Wall under Extreme Seismic Shear
# Vu = 3500kN (High), wall 3000x250
run_problem(11, "Extreme Seismic Shear (Vu=3500, 3m wall)", ShearWallDesign.design_shear, 
            Vu=3500.0, Pu=2000.0, lw=3000.0, hw=12000.0, tw=250.0, fc=30.0, fy=420.0)

# Problem 12: Short stubby wall (h/l = 0.5)
# Expected: alpha_c = 0.25 (higher capacity)
run_problem(12, "Stubby Shear Wall (h/l=0.5)", ShearWallDesign.design_shear, 
            Vu=1000.0, Pu=500.0, lw=4000.0, hw=2000.0, tw=200.0, fc=25.0, fy=420.0)

# Problem 13: Isolated Footing with high eccentricity (Uplift check)
# P=500, M=200. e = 0.4m. kernel L/6 = ??
run_problem(13, "Eccentric Footing (P=500, M=200)", IsolatedFootingDesign.design, 
            P=500.0, Mx=200.0, My=50.0, q_allow=150.0, fc=25.0, fy=420.0)

# Problem 14: Footing with very low soil capacity (q_allow=50 kPa)
# Expected: Large footing area
run_problem(14, "Soft Soil Footing (q_allow=50)", IsolatedFootingDesign.design, 
            P=1500.0, Mx=100.0, My=100.0, q_allow=50.0, fc=30.0, fy=420.0)

# Problem 15: Footing with Uplift (P < 0 if possible, or very large M)
# Expected: Should handle P being close to zero or negative
run_problem(15, "Uplift/Zero axial (P=10, M=300)", IsolatedFootingDesign.design, 
            P=10.0, Mx=300.0, My=0.0, q_allow=200.0, fc=25.0, fy=420.0)
