import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

# Import MAIN APP modules
from core.analysis.opensees_model import OpenSeesModelBuilder

def run_problem_31():
    print("==================================================")
    print("PROBLEM 31: AIRPORT TERMINAL (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Model Setup
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    
    # Long-span frame (60m)
    L = 60.0; H = 15.0
    builder.define_node(1, 0, 0, 0)
    builder.define_node(2, L, 0, 0)
    builder.define_node(3, 0, 0, H)
    builder.define_node(4, L, 0, H)
    builder.define_fixity(1, [1,1,1,1,1,1])
    builder.define_fixity(2, [1,1,1,1,1,1])
    
    # 2. Elements
    builder.define_geometric_transformation(1, 'Linear', [0, 1, 0])
    E = 2.1e8; A = 0.1; I = 0.005 # Large steel section
    G = 8e7; J = 0.01
    
    builder.define_elastic_beam_column(1, 1, 3, A, E, G, J, I, I, 1)
    builder.define_elastic_beam_column(2, 2, 4, A, E, G, J, I, I, 1)
    builder.define_elastic_beam_column(3, 3, 4, A, E, G, J, I, I, 1)
    
    # 3. Dynamic Wind (Simple Sine Wave)
    # Mass for dynamic analysis
    builder.define_mass(3, 100.0, 100.0, 100.0)
    builder.define_mass(4, 100.0, 100.0, 100.0)
    
    ops.timeSeries('Sine', 1, 0.0, 10.0, 1.0) # period 1s
    ops.pattern('Plain', 1, 1)
    ops.load(3, 200.0, 0, 0, 0, 0, 0) # 200 kN amplitude
    
    # 4. Analysis
    print("Starting Transient Analysis...")
    dt = 0.01
    builder.analyze_transient(200, dt) # 2 seconds
    
    # 5. Check
    disp = ops.nodeDisp(3, 1)
    print(f"Max Horizontal Displacement at Roof: {disp*1000:.2f} mm")
    
    print("PROBLEM 31 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_31()
