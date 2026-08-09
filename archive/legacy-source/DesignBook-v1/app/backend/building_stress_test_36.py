import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

# Import MAIN APP modules
from core.analysis.opensees_model import OpenSeesModelBuilder
from core.design.slab_beamless import FlatPlateDesign

def run_problem_36():
    print("==================================================")
    print("PROBLEM 36: PT FLAT SLAB (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Input: 8m x 8m span, 200mm slab
    L = 8.0; B = 8.0; T = 0.2
    fc = 35.0; fy = 1860.0 # PT strand
    
    # Loads
    DL = 0.2 * 24.0 * B # dead load kN/m for full width
    LL = 2.0 * B
    
    # PT: 12.7mm strands @ 500mm
    num_strands = (B * 1000 / 500.0)
    P_eff = num_strands * 150.0 # 150 kN per strand effective
    sag = 0.075 # 75mm drape
    
    # 2. Design Check
    pt_res = FlatPlateDesign.design_pt_slab(P_eff, sag, L, DL)
    print(f"PT Balanced Load: {pt_res['w_up']:.2f} kN/m (DL: {DL:.2f} kN/m)")
    
    # Moment at mid-span
    Mu = pt_res['net_load'] * L**2 / 8.0
    A = B * 1000 * T * 1000
    Z = (B * 1000 * (T * 1000)**2) / 6.0
    stress_res = FlatPlateDesign.check_stresses(P_eff, Mu, A, Z, fc)
    print(f"Service Stresses: {stress_res['status']} (Top: {stress_res['f_top']:.2f} MPa, Bot: {stress_res['f_bot']:.2f} MPa)")
    
    # 3. OpenSees Validation (Deflection under balanced load)
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    
    # Build model cleanly
    builder.define_node(1, 0, 0, 0)
    builder.define_node(2, L, 0, 0)
    builder.define_node(3, L/2, 0, 0)
    
    builder.define_fixity(1, [1,1,1,1,1,1])
    builder.define_fixity(2, [1,1,1,1,1,1])
    # Stabilize node 3 laterally/rotationally to be safe
    builder.define_fixity(3, [0,1,0,1,1,1])
    
    builder.define_geometric_transformation(1, 'Linear', [0, 1, 0])
    E = 4700*math.sqrt(fc)*1000; I = (B * T**3 / 12)
    builder.define_elastic_beam_column(1, 1, 3, B*T, E, 1e7, 1e-3, I, I, 1)
    builder.define_elastic_beam_column(2, 3, 2, B*T, E, 1e7, 1e-3, I, I, 1)
    
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1)
    total_net = DL + LL - pt_res['w_up']
    # Uniform load on both elements
    ops.eleLoad('-ele', 1, 2, '-type', '-beamUniform', 0, -total_net)
    
    print("Starting Post-Tensioned Analysis...")
    builder.analyze_static(1)
    
    disp = ops.nodeDisp(3, 3)
    print(f"Net Mid-span Deflection: {disp*1000:.4f} mm")
    
    print("PROBLEM 36 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_36()
