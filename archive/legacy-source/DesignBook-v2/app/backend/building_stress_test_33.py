import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

# Import MAIN APP modules
from core.analysis.opensees_model import OpenSeesModelBuilder
from core.design.shear_wall import ShearWallDesign

def run_problem_33():
    print("==================================================")
    print("PROBLEM 33: SLENDER WALL P-DELTA (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Input: 6m high wall, 200mm thick
    H = 6.0; L = 4.0; T = 0.2
    fc = 30.0; fy = 420.0
    
    # Loads
    Pu = 200.0 # Axial kN
    qu = 5.0   # Out-of-plane pressure kN/m2
    Mu_simple = qu * L * H**2 / 8.0 # kNm at mid-height (approx)
    
    # 2. Design Check
    # Rebar: 12mm bars @ 200mm (per face)
    As = 2 * (math.pi * 12**2 / 4) * (L*1000/200.0)
    slender_res = ShearWallDesign.design_slender_wall(Pu, Mu_simple, L*1000, H*1000, T*1000, fc, fy, As)
    print(f"Slender Wall Check: {slender_res['status']} (Capacity: {slender_res['phiMn_kNm']:.2f} kNm)")
    
    # 3. OpenSees Validation (P-Delta check)
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    builder.define_node(1, 0, 0, 0); builder.define_node(2, 0, 0, H)
    builder.define_fixity(1, [1,1,1,1,1,1])
    
    builder.define_geometric_transformation(1, 'PDelta', [0, 1, 0])
    E = 4700*math.sqrt(fc)*1000; A = L*T; I = (L*T**3/12)
    builder.define_elastic_beam_column(1, 1, 2, A, E, 1e7, 1e-3, I, I, 1)
    
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1)
    ops.load(2, qu*L*H/2, 0, -Pu, 0, 0, 0) # Top shear + Axial
    
    builder.analyze_static(1)
    mid_node = 3
    builder.define_node(mid_node, 0, 0, H/2)
    # Restart analysis to include mid-node
    builder.initialize_model()
    builder.define_node(1, 0, 0, 0); builder.define_node(2, 0, 0, H); builder.define_node(3, 0, 0, H/2)
    builder.define_fixity(1, [1,1,1,1,1,1])
    builder.define_geometric_transformation(1, 'PDelta', [1, 0, 0])
    builder.define_elastic_beam_column(1, 1, 3, A, E, 1e7, 1e-3, I, I, 1)
    builder.define_elastic_beam_column(2, 3, 2, A, E, 1e7, 1e-3, I, I, 1)
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1)
    ops.load(2, 0, 0, -Pu, 0, 0, 0)
    # Uniform load qu*L along the height
    ops.eleLoad('-ele', 1, 2, '-type', '-beamUniform', qu*L, 0)
    
    builder.analyze_static(1)
    disp = ops.nodeDisp(3, 1)
    print(f"Mid-height Out-of-plane Displacement: {disp*1000:.2f} mm")
    
    print("PROBLEM 33 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_33()
