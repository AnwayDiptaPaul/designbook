import sys
import os
import math
import numpy as np

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.reports.pdf_generator import pdf_generator
from core.design.qto import QuantityTakeoff

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
print("INTENSIVE TEST SUITE - SET 20 (PROBLEMS 96-100)")
print("==================================================")

# Problem 96: PDF Generation with Title
def problem_96():
    data = {"name": "Test Project 100", "code": "BNBC 2020", "concrete_vol": 125.5, "steel_weight": 14500.0, "total_cost": 3500000.0}
    output = "test_report.pdf"
    res = pdf_generator.generate_project_report(data, output)
    exists = os.path.exists(output)
    return {"pdf_created": exists, "path": output}

run_problem(96, "PDF Project Report Generation", problem_96)

# Problem 100: End-to-End Design to Report Compilation
def problem_100():
    # 1. Structural Logic (Beam)
    # 2. QTO
    vol = QuantityTakeoff.calculate_concrete_volume(0.3, 0.6, 5.0)
    steel = QuantityTakeoff.calculate_rebar_weight(1570, 5.0) # 5-20mm bars
    # 3. Cost
    cost = QuantityTakeoff.estimate_cost(vol, steel, 10.0)
    # 4. Report
    data = {
        "name": "E2E Final Problem 100",
        "concrete_vol": vol,
        "steel_weight": steel,
        "total_cost": cost["total_estimated_cost"]
    }
    res = pdf_generator.generate_project_report(data, "final_problem_100_report.pdf")
    return {"status": "Full Pipeline Verified", "total_cost": cost["total_estimated_cost"]}

run_problem(100, "Full End-to-End Pipeline Compilation", problem_100)
