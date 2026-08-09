import sys
import os
import math

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.design.beam import BeamDesign
from core.design.slab_oneway import OneWaySlabDesign

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
print("INTENSIVE TEST SUITE - SET 1 (PROBLEMS 1-5)")
print("==================================================")

# Problem 1: Very deep beam with extremely high moment
# Expected: Should return a high As_req or flag for compression reinforcement
run_problem(1, "Deep Beam (Mu=1200, 300x700)", BeamDesign.design_flexure, 
            Mu=1200.0, b=300.0, d=650.0, fc=30.0, fy=420.0)

# Problem 2: Under-sized beam (Small d for high moment)
# Expected: tension_controlled should be False, compression_reinforcement_needed should be True
run_problem(2, "Undersized Flexure (Mu=500, 250x400)", BeamDesign.design_flexure, 
            Mu=500.0, b=250.0, d=350.0, fc=25.0, fy=420.0)

# Problem 3: High Shear in thin web
# Expected: status should be "Section too small" or "FAIL"
run_problem(3, "High Shear (Vu=800, 250x500)", BeamDesign.design_shear, 
            Vu=800.0, b=250.0, d=450.0, fc=28.0, fy_vt=420.0)

# Problem 4: One-way slab with extreme live load (e.g. storage)
# Expected: valid As_req per meter strip
run_problem(4, "Heavy Load Slab (Mu=80, t=200)", OneWaySlabDesign.design_flexure, 
            Mu=80.0, t=200.0, fc=28.0, fy=420.0, cover=20.0, bar_dia=12.0)

# Problem 5: Beam with high strength concrete (fc=60 MPa)
# Expected: beta1 adjustment and higher capacity
run_problem(5, "HSC Beam (fc=60, Mu=600)", BeamDesign.design_flexure, 
            Mu=600.0, b=300.0, d=550.0, fc=60.0, fy=420.0)
