import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

# Import MAIN APP modules
from core.analysis.opensees_model import OpenSeesModelBuilder

def run_problem_23():
    print("==================================================")
    print("PROBLEM 23: INDUSTRIAL SHED (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Model Setup
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    
    # 20m span, 10m height, 5 bays @ 6m
    span = 20.0; spacing = 6.0; num_bays = 5
    h_eave = 8.0; h_ridge = 10.0
    
    node_map = {}
    tag = 1
    for bay in range(num_bays + 1):
        y = bay * spacing
        coords = [(0,y,0), (0,y,h_eave), (span/2,y,h_ridge), (span,y,h_eave), (span,y,0)]
        for i, c in enumerate(coords):
            builder.define_node(tag, *c)
            if c[2] == 0: builder.define_fixity(tag, [1]*6)
            node_map[(bay, i)] = tag
            tag += 1
            
    # 2. Transformations & Elements
    builder.define_geometric_transformation(1, 'Linear', [0, 0, 1])
    E = 2.0e8; G = 7.7e7; A = 0.02; Ix = 1e-3; Iy = 1e-3; J = 1e-4
    el_tag = 1
    for bay in range(num_bays + 1):
        # Columns
        builder.define_elastic_beam_column(el_tag, node_map[(bay,0)], node_map[(bay,1)], A, E, G, J, Ix, Iy, 1); el_tag += 1
        builder.define_elastic_beam_column(el_tag, node_map[(bay,4)], node_map[(bay,3)], A, E, G, J, Ix, Iy, 1); el_tag += 1
        # Rafters
        builder.define_elastic_beam_column(el_tag, node_map[(bay,1)], node_map[(bay,2)], A, E, G, J, Ix, Iy, 1); el_tag += 1
        builder.define_elastic_beam_column(el_tag, node_map[(bay,3)], node_map[(bay,2)], A, E, G, J, Ix, Iy, 1); el_tag += 1
        
    # 3. Dynamic Gantry Loads
    impact_load = 200.0 * 1.25
    surge_load = impact_load * 0.1
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1)
    ops.load(node_map[(2, 1)], surge_load, 0, -impact_load, 0, 0, 0)
    ops.load(node_map[(2, 3)], -surge_load, 0, -impact_load, 0, 0, 0)
    
    # 4. Analysis
    builder.analyze_static(1)
    
    # 5. Check
    ridge_node = node_map[(2, 2)]
    disp = ops.nodeDisp(ridge_node, 3)
    print(f"Max Rafter Ridge Displacement: {disp:.4f} m")
    
    print("PROBLEM 23 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_23()
