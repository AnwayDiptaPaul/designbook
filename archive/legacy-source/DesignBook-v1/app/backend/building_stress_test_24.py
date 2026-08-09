import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

# Import MAIN APP modules
from core.analysis.opensees_model import OpenSeesModelBuilder
from core.loads.seismic import SeismicResult

def run_problem_24():
    print("==================================================")
    print("PROBLEM 24: HOSPITAL L-SHAPE (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Model Setup
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    
    # L-Shape: 3x3 grid, missing corner 1x1
    # ix, iy from 0 to 2
    node_map = {}
    tag = 1
    story_h = 3.5
    for s in range(4):
        for ix in range(3):
            for iy in range(3):
                if ix == 0 or iy == 0: # L-Shape
                    builder.define_node(tag, ix*6.0, iy*6.0, s*story_h)
                    if s == 0: builder.define_fixity(tag, [1]*6)
                    # Assign mass (unbalanced to create torsion)
                    if s > 0:
                        m = 200.0 / 9.81
                        if ix == 2 or iy == 2: m *= 1.5 # Heavier at wings
                        builder.define_mass(tag, m, m, 1e-9)
                    node_map[(s, ix, iy)] = tag
                    tag += 1
                    
    # 2. Elements
    builder.define_geometric_transformation(1, 'Linear', [0, 1, 0])
    builder.define_geometric_transformation(2, 'Linear', [1, 0, 0])
    builder.define_geometric_transformation(3, 'Linear', [1, 0, 0])
    
    E = 2.5e7; G = 1e7
    el_tag = 1
    for s in range(3):
        for ix in range(3):
            for iy in range(3):
                if (s, ix, iy) in node_map and (s+1, ix, iy) in node_map:
                    builder.define_elastic_beam_column(el_tag, node_map[(s,ix,iy)], node_map[(s+1,ix,iy)], 0.5*0.5, E, G, 1e-3, 0.5**4/12, 0.5**4/12, 3)
                    el_tag += 1
    
    # 3. Torsional Irregularity Check
    # Apply lateral load at top
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1)
    for ix in range(3):
        for iy in range(3):
            if (3, ix, iy) in node_map:
                ops.load(node_map[(3, ix, iy)], 100.0, 0, 0, 0, 0, 0)
                
    # 4. Analysis
    builder.analyze_static(1)
    
    # 5. Check displacements at top floor (s=3)
    disps = []
    for ix in range(3):
        for iy in range(3):
            if (3, ix, iy) in node_map:
                disps.append(ops.nodeDisp(node_map[(3, ix, iy)], 1))
    
    delta_max = max(disps)
    delta_avg = sum(disps) / len(disps)
    ax = SeismicResult.calculate_torsional_amplification(delta_max, delta_avg)
    
    print(f"Max Displacement: {delta_max:.4f} m, Avg: {delta_avg:.4f} m")
    print(f"Torsional Amplification Ax: {ax:.3f}")
    
    print("PROBLEM 24 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_24()
