import sys
import os
import math

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.design.detailing import DetailingDesign

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
print("INTENSIVE TEST SUITE - SET 9 (PROBLEMS 41-45)")
print("==================================================")

# Problem 41: Tension Development Length (db=20, fy=420, fc=25)
run_problem(41, "Tension Development Length (20mm bar)", DetailingDesign.calculate_development_length_tension, 
            db=20.0, fy=420.0, fc=25.0, psi_t=1.3) # Top bar factor

# Problem 42: Hooked Development Length
run_problem(42, "Hooked Development Length (16mm bar)", DetailingDesign.calculate_hook_development_length, 
            db=16.0, fy=420.0, fc=25.0)

# Problem 43: Class B Lap Splice
ld_val = 800.0
run_problem(43, "Class B Lap Splice (ld=800)", DetailingDesign.calculate_lap_splice_tension, 
            ld=ld_val, splice_class="B")

# Problem 44: Min Spacing (db=25, s=60)
run_problem(44, "Min Spacing Check (db=25, s=60)", DetailingDesign.check_min_spacing, 
            db=25.0, s_center=60.0, aggravate_size=20.0)

# Problem 45: Tight Spacing (db=25, s=40)
run_problem(45, "Tight Spacing fail (db=25, s=45)", DetailingDesign.check_min_spacing, 
            db=25.0, s_center=45.0, aggravate_size=20.0)
