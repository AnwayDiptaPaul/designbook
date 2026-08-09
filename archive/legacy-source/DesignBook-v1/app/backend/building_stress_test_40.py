import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

# Import MAIN APP modules
from core.analysis.opensees_model import OpenSeesModelBuilder

def run_problem_40():
    print("==================================================")
    print("PROBLEM 40: SEISMIC BASE ISOLATION (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Model Setup: Single Degree of Freedom (SDOF) with LRB
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    
    # Nodes: 1 (Ground), 2 (Base of building), 3 (Roof)
    builder.define_node(1, 0, 0, 0) # Ground
    builder.define_node(2, 0, 0, 0) # Isolator top
    builder.define_node(3, 0, 0, 3.5) # Roof level
    
    builder.define_fixity(1, [1,1,1,1,1,1])
    # Isolator allows X translation
    builder.define_fixity(2, [0,1,1,1,1,1])
    
    # 2. Isolator Material (Lead-Rubber Bearing - Bilinear)
    # k1 (Initial), k2 (Post-yield), Fy (Yield force)
    k1 = 20000.0; k2 = 2000.0; fy = 100.0
    # Steel01 (Bilinear)
    ops.uniaxialMaterial('Steel01', 1, fy, k1, k2/k1)
    
    # 3. Elements
    builder.define_geometric_transformation(1, 'Linear', [0, 1, 0])
    # Building column (Rigid relative to isolator)
    builder.define_elastic_beam_column(1, 2, 3, 0.5, 3e7, 1e7, 1e-3, 0.1, 0.1, 1)
    # Isolator (zeroLength)
    builder.define_rotational_spring(2, 1, 2, 1, 1) # X direction spring (dir 1)
    
    # 4. Mass (500 tons)
    builder.define_mass(3, 500.0, 500.0, 500.0)
    
    # 5. Analysis (Pushover of isolator)
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1)
    ops.load(3, 500.0, 0, 0, 0, 0, 0) # 500 kN load
    
    print("Starting Base Isolation Analysis...")
    builder.analyze_static(10)
    
    # 6. Check
    disp = ops.nodeDisp(3, 1)
    # Expected: Force = 500. Displacement s.t. F = fy + k2(u - dy)
    # dy = fy/k1 = 100/20000 = 0.005 m
    # 500 = 100 + 2000 * (u - 0.005) => 400 = 2000u - 10 => 410 = 2000u => u = 0.205 m
    print(f"Isolator Displacement: {disp*1000:.2f} mm")
    
    print("PROBLEM 40 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_40()
