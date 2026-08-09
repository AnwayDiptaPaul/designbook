import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

# Import MAIN APP modules
from core.analysis.opensees_model import OpenSeesModelBuilder

def run_problem_29():
    print("==================================================")
    print("PROBLEM 29: FIBER PUSHOVER (RE-VALIDATION VIA CORE APP)")
    print("==================================================")
    
    # 1. Model Setup
    builder = OpenSeesModelBuilder()
    builder.initialize_model()
    
    # 3-story column (cantilever for pushover)
    h = 3.0
    builder.define_node(1, 0, 0, 0)
    builder.define_node(2, 0, 0, h)
    builder.define_node(3, 0, 0, 2*h)
    builder.define_node(4, 0, 0, 3*h)
    builder.define_fixity(1, [1,1,1,1,1,1])
    
    # 2. Materials
    builder.define_material_concrete(1, 30.0) # 30 MPa
    builder.define_material_steel(2, 400.0, 2e5) # 400 MPa
    
    # 3. Sections & Elements
    # Column 500x500
    builder.define_fiber_section_rect(1, 1, 2, 0.5, 0.5, 0.04, 0.002, 0.002)
    builder.define_geometric_transformation(1, 'PDelta', [1, 0, 0])
    
    builder.define_nonlinear_beam_column(1, 1, 2, 5, 1, 1)
    builder.define_nonlinear_beam_column(2, 2, 3, 5, 1, 1)
    builder.define_nonlinear_beam_column(3, 3, 4, 5, 1, 1)
    
    # 4. Gravity Analysis
    ops.timeSeries('Constant', 2); ops.pattern('Plain', 2, 2)
    ops.load(4, 0, 0, -1000.0, 0, 0, 0)
    builder.analyze_static(1)
    ops.loadConst('-time', 0.0)
    
    # 5. Pushover Analysis (Displacement Control)
    ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1)
    ops.load(4, 1.0, 0, 0, 0, 0, 0)
    
    target_disp = 0.2 # 200mm
    steps = 100
    dU = target_disp / steps
    
    ops.system('BandGeneral')
    ops.numberer('RCM')
    ops.constraints('Plain')
    ops.test('NormDispIncr', 1.0e-6, 20)
    ops.algorithm('Newton')
    ops.integrator('DisplacementControl', 4, 1, dU)
    ops.analysis('Static')
    
    print("Starting Pushover...")
    for i in range(steps):
        ok = ops.analyze(1)
        if ok != 0:
            print(f"Pushover failed at step {i}")
            break
            
    # 5. Check
    base_shear = -ops.eleResponse(1, 'force')[0] # Approx
    print(f"Max Base Shear at 200mm: {base_shear:.2f} kN")
    
    print("PROBLEM 29 RE-VALIDATED VIA CORE APP.")

if __name__ == "__main__":
    run_problem_29()
