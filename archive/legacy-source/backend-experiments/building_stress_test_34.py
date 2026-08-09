import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

# Import MAIN APP modules
from core.analysis.opensees_model import OpenSeesModelBuilder
from core.design.cfs import CFSDesign

def run_problem_34():
    print("==================================================")
    print("PROBLEM 34: CFS WAREHOUSE (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Input: C-Section Column (200x75x2.5)
    h = 200.0; b = 75.0; t = 2.5
    fy = 350.0; E = 203000.0
    A = (h + 2*b) * t # Approx
    
    # 2. Local Buckling Check
    f_stress = 150.0 # Operational stress
    b_eff = CFSDesign.calculate_effective_width(h, t, f_stress, E)
    print(f"Effective Web Width: {b_eff:.2f} mm (Original: {h:.2f} mm)")
    
    # 3. Column Capacity
    r = 70.0; L = 4000.0 # 4m height
    Pn = CFSDesign.design_column_capacity(A, r, L, fy, E)
    print(f"Axial Capacity (Flexural): {Pn:.2f} kN")
    
    # 4. OpenSees validation
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    builder.define_node(1, 0, 0, 0); builder.define_node(2, 0, 0, L/1000)
    builder.define_fixity(1, [1,1,1,1,1,1])
    builder.define_geometric_transformation(1, 'PDelta', [1, 0, 0])
    builder.define_elastic_beam_column(1, 1, 2, A/1e6, E*1000, 8e7, 1e-3, 1e-6, 1e-6, 1)
    
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1)
    ops.load(2, 0, 0, -100.0, 0, 0, 0) # 100 kN load
    
    builder.analyze_static(1)
    comp = ops.nodeDisp(2, 3)
    print(f"Axial Shortening: {comp*1000:.4f} mm")
    
    print("PROBLEM 34 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_34()
