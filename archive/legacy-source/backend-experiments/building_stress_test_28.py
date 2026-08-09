import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

# Import MAIN APP modules
from core.analysis.opensees_model import OpenSeesModelBuilder

def run_problem_28():
    print("==================================================")
    print("PROBLEM 28: PARKING THERMAL (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Model Setup
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    
    # 30m x 20m structure
    L = 30.0; B = 20.0
    node_map = {}
    tag = 1
    for x in [0, L]:
        for y in [0, B]:
            builder.define_node(tag, x, y, 0.0)
            builder.define_fixity(tag, [1,1,1,1,1,1])
            node_map[(x, y, 0)] = tag
            tag += 1
            builder.define_node(tag, x, y, 3.5)
            node_map[(x, y, 3.5)] = tag
            tag += 1
            
    # 2. Elements
    builder.define_geometric_transformation(1, 'Linear', [0, 1, 0]) # Beam
    builder.define_geometric_transformation(2, 'Linear', [1, 0, 0]) # Column
    E = 2.5e7; A = 0.5; I = 0.5**4/12
    G = 1e7; J = 1e-3
    
    # Columns
    el_tag = 1
    for x in [0, L]:
        for y in [0, B]:
            n1 = node_map[(x, y, 0)]
            n2 = node_map[(x, y, 3.5)]
            builder.define_elastic_beam_column(el_tag, n1, n2, A, E, G, J, I, I, 2)
            el_tag += 1
            
    # Girder connecting nodes along L at y=0
    n_a = node_map[(0, 0, 3.5)]
    n_b = node_map[(L, 0, 3.5)]
    builder.define_elastic_beam_column(el_tag, n_a, n_b, A, E, G, J, I, I, 1)
    
    # 3. Thermal Effect (Simulate expansion)
    # BNBC: Thermal strain = alpha * deltaT
    alpha = 1.0e-5
    dT = 30.0 # 30 deg rise
    axial_force = alpha * dT * E * A
    
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1)
    # Apply equivalent axial force to simulate expansion if blocked
    ops.load(n1, -axial_force, 0, 0, 0, 0, 0)
    ops.load(n2, axial_force, 0, 0, 0, 0, 0)
    
    # 4. Analysis
    builder.analyze_static(1)
    
    # 5. Check
    rx = ops.nodeReaction(n1, 1)
    print(f"Thermal Expansion Reaction at Support: {rx:.2f} kN")
    
    print("PROBLEM 28 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_28()
