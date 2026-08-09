import sys
import os
import math

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.design.serviceability import ServiceabilityDesign

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
print("INTENSIVE TEST SUITE - SET 8 (PROBLEMS 36-40)")
print("==================================================")

# Problem 36: Effective Inertia (Branson)
# Ig=1e9, Icr=4e8, Mcr=30, Ma=50
run_problem(36, "Branson Effective Inertia (Ma > Mcr)", ServiceabilityDesign.calculate_effective_inertia, 
            Mcr=30.0, Ma=50.0, Ig=1.0e9, Icr=4.0e8)

# Problem 37: Long-term multiplier
# 5 years (xi=2.0), 1% compression steel (rho_prime=0.01)
run_problem(37, "Long-term Deflection Multiplier", ServiceabilityDesign.calculate_long_term_deflection_multiplier, 
            xi=2.0, rho_prime=0.01)

# Problem 38: Crack Width (Gergely-Lutz)
# fs=250MPa, dc=50mm, A=2500 mm2
run_problem(38, "Crack Width (fs=250, dc=50)", ServiceabilityDesign.check_crack_width, 
            fs=250.0, dc=50.0, A=2500.0)

# Problem 39: Floor Vibration (Hospitals/Offices freq > 4Hz)
# E=30GPa, I=0.005m4, L=8m, m=800kg/m
run_problem(39, "Floor Vibration (fn check)", ServiceabilityDesign.calculate_beam_frequency, 
            E=3.0e10, I=0.005, L=8.0, mass_per_meter=800.0)

# Problem 40: Effective Inertia (Ma < Mcr - should return Ig)
run_problem(40, "Effective Inertia (No Cracking)", ServiceabilityDesign.calculate_effective_inertia, 
            Mcr=40.0, Ma=20.0, Ig=1.0e9, Icr=4.0e8)
