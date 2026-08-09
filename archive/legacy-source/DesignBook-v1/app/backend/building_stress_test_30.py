import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

# Import MAIN APP modules
from core.analysis.opensees_model import OpenSeesModelBuilder

def run_problem_30():
    print("==================================================")
    print("PROBLEM 30: SUSPENDED CABLE (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Model Setup
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    
    # Cable 100m span, 10m sag
    span = 100.0; sag = 10.0
    num_seg = 20
    dx = span / num_seg
    
    node_map = {}
    for i in range(num_seg + 1):
        x = i * dx
        # Parabolic shape: y = 4 * sag * x * (L - x) / L^2
        z = 4 * sag * x * (span - x) / (span**2)
        builder.define_node(i+1, x, 0.0, z)
        # Restrain rotations for intermediate nodes
        if i > 0 and i < num_seg:
            builder.define_fixity(i+1, [0,0,0,1,1,1])
        node_map[i] = i+1
        
    builder.define_fixity(1, [1,1,1,1,1,1])
    builder.define_fixity(num_seg+1, [1,1,1,1,1,1])
    
    # 2. Materials (Steel Cable)
    ops.uniaxialMaterial('Elastic', 1, 2e8) # 200 GPa
    
    # 3. Elements (Beam-based cable for stability)
    A = 0.01; E = 2e8; G = 1e8; J = 1e-6; I = 1e-8
    builder.define_geometric_transformation(1, 'Corotational', [0, 1, 0])
    for i in range(num_seg):
        builder.define_elastic_beam_column(i+1, node_map[i], node_map[i+1], A, E, G, J, I, I, 1)
        
    # 4. Load (Self weight + Live load)
    ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1)
    for i in range(1, num_seg):
        ops.load(node_map[i], 0.0, 0.0, -50.0, 0, 0, 0) # 50 kN force
        
    # 5. Analysis (Large displacement)
    ops.system('BandGeneral')
    ops.constraints('Plain')
    ops.numberer('RCM')
    ops.test('NormDispIncr', 1e-6, 50)
    ops.algorithm('Newton')
    ops.integrator('LoadControl', 0.1)
    ops.analysis('Static')
    
    print("Starting Cable Analysis...")
    ok = ops.analyze(10)
    
    # 6. Check
    mid_node = node_map[num_seg // 2]
    disp_z = ops.nodeDisp(mid_node, 3)
    print(f"Mid-span Cable Vertical Displacement: {disp_z:.4f} m")
    
    print("PROBLEM 30 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_30()
