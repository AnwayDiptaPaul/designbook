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

def run_problem_25():
    print("==================================================")
    print("PROBLEM 25: BASEMENT RETAINING (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Input
    h = 6.0
    inp = RetainingWallInput(height_m=h, soil_gamma=18.0, soil_phi=30.0, surcharge_kpa=20.0, water_table_depth_m=3.0)
    
    # 2. Design Module check
    pressures = RetainingWallDesign.calculate_lateral_pressures(inp)
    for p in pressures:
        print(f"Depth {p['depth']}m: Pressure {p['pressure_kpa']:.2f} kPa")
        
    # 3. Structural Analysis check
    builder = OpenSeesModelBuilder(ndm=2, ndf=3)
    builder.initialize_model()
    
    # Material/Transf
    builder.define_geometric_transformation(1, 'Linear', [0]) # 2D dummy vec
    E = 2.5e7; A = 0.3; I = 0.3**3/12
    
    for i, p in enumerate(pressures):
        builder.define_node(i+1, 0.0, h - p['depth'])
        if i == len(pressures) - 1: builder.define_fixity(i+1, [1,1,1])
        if i > 0:
            builder.define_elastic_beam_column(i, i, i+1, A, E, E*0.4, 0, I, I, 1) # 2D: J, Iy unused
        
    # Apply loads
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1)
    for i, p in enumerate(pressures):
        ops.load(i+1, p['pressure_kpa'], 0, 0)
        
    builder.analyze_static(1)
    
    disp = ops.nodeDisp(1, 1)
    print(f"Max Wall Deflection at top: {disp:.4f} m")
    
    print("PROBLEM 25 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_25()
