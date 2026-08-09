import sys
import os
import math

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.design.slab_twoway import TwoWaySlabDesign
from core.design.slab_beamless import FlatPlateDesign

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
print("INTENSIVE TEST SUITE - SET 4 (PROBLEMS 16-20)")
print("==================================================")

# Problem 16: Two-way Slab with high moment (Mu=120 kNm/m)
run_problem(16, "Two-way Slab High Moment (Mu=120, t=200)", TwoWaySlabDesign.design_flexure_fea, 
            Mu_x=120.0, Mu_y=80.0, t=200.0, fc=28.0, fy=420.0)

# Problem 17: Punching Shear (Interior Column)
# Vu = 800kN, col 400x400, slab t=200 (d=160)
run_problem(17, "Punching Interior (Vu=800, c=400, t=200)", FlatPlateDesign.check_punching_shear, 
            Vu=800.0, Mu_unbalanced=50.0, c1=400.0, c2=400.0, d=160.0, fc=28.0, location="interior")

# Problem 18: Punching Shear (Corner Column)
# Corner b0 = c1+d/2 + c2+d/2 = 400+80 + 400+80 = 960 (actually if col is at corner)
run_problem(18, "Punching Corner (Vu=300, c=400, t=200)", FlatPlateDesign.check_punching_shear, 
            Vu=300.0, Mu_unbalanced=20.0, c1=400.0, c2=400.0, d=160.0, fc=30.0, location="corner")

# Problem 19: High Strength Concrete Punching (fc=50)
run_problem(19, "HSC Punching (fc=50, Vu=1500)", FlatPlateDesign.check_punching_shear, 
            Vu=1500.0, Mu_unbalanced=100.0, c1=500.0, c2=500.0, d=200.0, fc=50.0, location="interior")

# Problem 20: Very Thin Slab Punching (t=125)
run_problem(20, "Thin Slab Punching (t=125, d=90)", FlatPlateDesign.check_punching_shear, 
            Vu=250.0, Mu_unbalanced=0.0, c1=300.0, c2=300.0, d=90.0, fc=25.0, location="interior")
