import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

# Import MAIN APP modules
from core.analysis.opensees_model import OpenSeesModelBuilder
from core.design.column import ColumnDesign

def run_problem_32():
    print("==================================================")
    print("PROBLEM 32: SHEAR-TORSION COLUMN (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Input: High-strength column (60 MPa)
    fc = 60.0; fy = 500.0
    b = 600.0; h = 600.0; d = 540.0
    
    # Loads
    Pu = 2000.0 # kN
    Vu = 400.0  # kN
    Tu = 50.0   # kNm
    
    # 2. Design Checks
    # Rebar: 10mm stirrups @ 100mm (2 legs)
    av = 2 * (math.pi * 10**2 / 4)
    shear_res = ColumnDesign.design_shear(Vu, b, d, fc, fy, av, 100.0)
    print(f"Shear Check: {shear_res['status']} (Capacity: {shear_res['phiVn']:.2f} kN)")
    
    # Torsion: 10mm ties @ 100mm
    torsion_res = ColumnDesign.design_torsion(Tu, Vu, b, h, fc, fy, av/2, 100.0, 2000.0)
    print(f"Torsion Check: {torsion_res['status']} (Threshold: {torsion_res['T_threshold']:.2f} kNm)")
    
    # 3. OpenSees Validation (Purely axial for drift check)
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    builder.define_node(1, 0, 0, 0); builder.define_node(2, 0, 0, 4.0)
    builder.define_fixity(1, [1,1,1,1,1,1])
    builder.define_geometric_transformation(1, 'Linear', [1, 0, 0])
    builder.define_elastic_beam_column(1, 1, 2, b*h/1e6, 4700*math.sqrt(fc)*1000, 1e7, 1e-3, (b*h**3/12)/1e12, (h*b**3/12)/1e12, 1)
    
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1)
    ops.load(2, Vu, 0, -Pu, 0, 0, Tu)
    
    builder.analyze_static(1)
    drift = ops.nodeDisp(2, 1) / 4.0
    print(f"Drift Ratio: {drift:.4f}")
    
    print("PROBLEM 32 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_32()
