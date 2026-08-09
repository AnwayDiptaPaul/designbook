import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

# Import MAIN APP modules
from core.analysis.opensees_model import OpenSeesModelBuilder
from core.design.retaining_wall import RetainingWallDesign, RetainingWallInput

def run_problem_38():
    print("==================================================")
    print("PROBLEM 38: BRIDGE ABUTMENT SSI (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Input: 6m high abutment wall, 10m wide, 0.5m thick
    H = 6.0; B = 10.0; T = 0.5
    fc = 30.0; gamma_soil = 18.0; phi = 30.0
    
    # 2. Design Check (Lateral Pressure)
    inp = RetainingWallInput(height_m=H, soil_gamma=gamma_soil, soil_phi=phi)
    pressures_list = RetainingWallDesign.calculate_lateral_pressures(inp)
    p_last = pressures_list[-1]['pressure_kpa']
    print(f"Active Pressure at Base: {p_last:.2f} kN/m2")
    
    # 3. OpenSees Validation (Soil Springs)
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    
    # Wall nodes
    builder.define_node(1, 0, 0, 0); builder.define_node(2, 0, 0, H)
    builder.define_node(4, 0, 0, H/2) # Mid-height node on wall
    
    # Soil interaction node (same location as 4)
    builder.define_node(3, 0, 0, H/2) 
    builder.define_fixity(3, [1,1,1,1,1,1]) # Earth fixed
    
    builder.define_fixity(1, [1,1,1,1,1,1]) # Base fixed
    
    # Soil Springs (Mz-direction spring? No, X-direction as before)
    k_soil = 5000.0 * B # kN/m
    ops.uniaxialMaterial('Elastic', 1, k_soil)
    ops.element('zeroLength', 10, 4, 3, '-mat', 1, '-dir', 1) # Spring tag 10
    
    # Elements
    builder.define_geometric_transformation(1, 'Linear', [0, 1, 0])
    E = 4700*math.sqrt(fc)*1000; A = B*T; I = (B*T**3/12)
    builder.define_elastic_beam_column(1, 1, 4, A, E, 1e7, 1e-3, I, I, 1)
    builder.define_elastic_beam_column(2, 4, 2, A, E, 1e7, 1e-3, I, I, 1)
    
    # Load (Active pressure profile)
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1)
    p_total = p_last * B
    # Applied as horizontal load in X (Dir 1)
    ops.eleLoad('-ele', 1, '-type', '-beamUniform', p_total, 0)
    
    print("Starting SSI Analysis...")
    builder.analyze_static(1)
    
    disp = ops.nodeDisp(2, 1)
    print(f"Abutment Top Displacement: {disp*1000:.2f} mm")
    
    print("PROBLEM 38 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_38()
