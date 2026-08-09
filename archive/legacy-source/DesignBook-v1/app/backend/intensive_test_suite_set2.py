import sys
import os
import math

print("DEBUG: Startup...")

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))
print(f"DEBUG: sys.path[0] = {sys.path[0]}")

print("DEBUG: Importing ColumnDesign...")
from core.design.column import ColumnDesign
print("DEBUG: Import successful.")

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
print("INTENSIVE TEST SUITE - SET 2 (PROBLEMS 6-10)")
print("==================================================")

# Problem 6: Slender Column
print("Problem 6: Slender Column Magnification")
M_orig = 100.0
# klu/r = 50 (Very slender)
M_mag = ColumnDesign.magnify_moments(Mu=M_orig, Pu=1000.0, Ag=400*400, fc=28.0, klu_over_r=50.0)
print(f"Original M: {M_orig}, Magnified M: {M_mag:.2f}")

# Problem 7: Biaxial Bending
print("\nProblem 7: Biaxial Bending capacity")
rebar = [{"depth": 60, "As": 1200}, {"depth": 340, "As": 1200}]
diag_res = ColumnDesign.generate_interaction_diagram(400, 400, 28, 420, rebar)
diag_x = diag_res["points"]
diag_y = diag_x # Symmetrical for test
print(f"Generated diagram with {len(diag_x)} points")
biax = ColumnDesign.check_biaxial_capacity(Pu=800.0, Mux=40.0, Muy=40.0, diagram_x=diag_x, diagram_y=diag_y)
print(f"Biaxial Check (Pu=800, Mux=40, Muy=40): {biax}")

# Problem 8: High Axial Load (Over capacity)
print("\nProblem 8: High Axial Load")
# P_max for 400x400 with 1% steel is ~3000kN
axial_fail = ColumnDesign.check_biaxial_capacity(Pu=4500.0, Mux=10.0, Muy=10.0, diagram_x=diag_x, diagram_y=diag_y)
print(f"High Axial result: {axial_fail}")

# Problem 9: Thin Column Slenderness check
print("\nProblem 9: Thin Column slenderness check")
is_slender = ColumnDesign.check_slenderness(klu_over_r=45.0, M1=50.0, M2=100.0, is_sway=False)
print(f"Slenderness Check (klu/r=45, Non-sway): {'STATIONARY' if is_slender else 'SLENDER'}")

# Problem 10: High Strength Column (fc=80)
print("\nProblem 10: High Strength Concrete Column")
hsc_diag = ColumnDesign.generate_interaction_diagram(400, 400, 80, 420, rebar)["points"]
print(f"HSC Pure Compression P: {hsc_diag[0]['P']:.2f} kN")
