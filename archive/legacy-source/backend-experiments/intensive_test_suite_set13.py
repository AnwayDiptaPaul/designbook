import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.analysis.opensees_model import OpenSeesModelBuilder

def run_problem(id, title, func, **kwargs):
    print(f"\n--- Problem {id}: {title} ---")
    try:
        res = func(**kwargs)
        print(f"Outcome: {res}")
        return res
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

print("==================================================")
print("INTENSIVE TEST SUITE - SET 13 (PROBLEMS 61-65)")
print("==================================================")

# Problem 61: Fiber Section Moment-Curvature
def problem_61():
    model = OpenSeesModelBuilder(ndm=2, ndf=3)
    model.initialize_model()
    
    # Material: fc=30, fy=420
    model.define_material_concrete(1, 30.0)
    model.define_material_steel(2, 420.0, 2e5)
    
    # Section: 300x500mm, 2-20mm top, 3-20mm bot (As_top=628, As_bot=942)
    model.define_fiber_section_rect(1, 1, 2, 500.0, 300.0, 60.0, 628.0, 942.0)
    
    # Single element cantilever (1m)
    model.define_node(1, 0, 0, 0)
    model.define_node(2, 1000.0, 0, 0)
    model.define_fixity(1, [1, 1, 1])
    
    ops.geomTransf('Linear', 1)
    model.define_nonlinear_beam_column(1, 1, 2, 5, 1, 1)
    
    # Apply Moment
    ops.timeSeries('Linear', 1)
    ops.pattern('Plain', 1, 1)
    ops.load(2, 0, 0, 1.0e8) # 100 kNm
    
    status = model.analyze_static(10)
    
    # Displacement at tip
    disp = ops.nodeDisp(2, 3) # rotation in 2D
    return {"status": "success" if status == 0 else "failed", "rotation_rad": disp}

run_problem(61, "Fiber Section Moment-Curvature", problem_61)

# Problem 62: Confined Concrete Behavior
def problem_62():
    # Comparing fc with different ductility parameters (epsu)
    ops.wipe(); ops.model('basic', '-ndm', 1, '-ndf', 1)
    ops.node(1, 0); ops.node(2, 0); ops.fix(1, 1)
    # Material 1: Unconfined (epsu=0.005)
    ops.uniaxialMaterial('Concrete01', 1, -30.0, -0.002, 0.0, -0.005)
    # Material 2: Confined (epsu=0.02)
    ops.uniaxialMaterial('Concrete01', 2, -30.0, -0.002, -10.0, -0.02)
    
    # Test Material 1
    ops.element('zeroLength', 1, 1, 2, '-mat', 1, '-dir', 1)
    ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1); ops.load(2, -1.0)
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral')
    ops.test('NormDispIncr', 1.0e-8, 10); ops.algorithm('KrylovNewton')
    ops.integrator('DisplacementControl', 2, 1, -0.0001)
    ops.analysis('Static'); ops.analyze(60) # push to 0.006 strain
    
    ops.reactions()
    force1 = ops.nodeReaction(1, 1)
    return {"unconfined_force_at_0.006": force1}

run_problem(62, "Confined Concrete Model (Concrete01)", problem_62)

# Problem 64: P-M Interaction in Fiber Column
def problem_64():
    # Axially loaded column + Lateral load
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    ops.node(1,0,0); ops.node(2,0,3000.0); ops.fix(1,1,1,1)
    ops.uniaxialMaterial('Concrete01', 1, -30.0, -0.002, 0.0, -0.005)
    ops.uniaxialMaterial('Steel01', 2, 420.0, 2e5, 0.01)
    
    # Fiber section 400x400
    ops.section('Fiber', 1)
    ops.patch('rect', 1, 10, 10, -200, -200, 200, 200)
    ops.layer('straight', 2, 4, 200.0, 150, -150, 150, 150)
    ops.layer('straight', 2, 4, 200.0, -150, -150, -150, 150)
    
    ops.geomTransf('PDelta', 1)
    ops.beamIntegration('Lobatto', 1, 1, 5)
    ops.element('forceBeamColumn', 1, 1, 2, 1, 1)
    
    # Gravity
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1); ops.load(2, 0, -1e6, 0) # 1000kN axial
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral')
    ops.test('NormDispIncr', 1.0e-8, 10); ops.algorithm('Newton')
    ops.analysis('Static'); ops.analyze(1)
    
    # Lateral
    ops.timeSeries('Linear', 2); ops.pattern('Plain', 2, 2); ops.load(2, 1.0, 0, 0)
    ops.integrator('DisplacementControl', 2, 1, 1.0)
    ops.analyze(50) # push to 50mm
    
    ops.reactions()
    base_shear = ops.nodeReaction(1, 1)
    return {"base_shear_at_50mm": -base_shear}

run_problem(64, "Fiber Column P-M Response", problem_64)
