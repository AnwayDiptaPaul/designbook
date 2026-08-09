import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.analysis.nonlinear_hinge import NonlinearPushoverAnalysis

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
print("INTENSIVE TEST SUITE - SET 11 (PROBLEMS 51-55)")
print("==================================================")

# Problem 51: Plastic Hinge Yielding (Simple Cantilever)
def problem_51():
    ops.wipe(); ops.model('basic', '-ndm', 3, '-ndf', 6)
    # Using small distance between nodes for ZeroLength or use a better model
    ops.node(1,0,0,0); ops.node(2,0,0,0); ops.node(3,0,0,3)
    ops.fix(1,1,1,1,1,1,1) # Tag 1, 6 DOFs
    # Hinge at base
    ops.uniaxialMaterial('Steel01', 1, 100.0, 1.0e8, 0.01)
    ops.element('zeroLength', 1, 1, 2, '-mat', 1, '-dir', 5) # RY
    # Constrain other DOFs of 2 to 1
    ops.equalDOF(1, 2, 1, 2, 3, 4, 6) # X, Y, Z, RX, RZ
    
    ops.geomTransf('Linear', 1, 0, 1, 0)
    ops.element('elasticBeamColumn', 2, 2, 3, 0.1, 2e8, 8e7, 1e-4, 1e-4, 1e-4, 1)
    
    ops.timeSeries('Linear', 1)
    ops.pattern('Plain', 1, 1)
    ops.load(3, 1.0, 0, 0, 0, 0, 0) 
    
    res = NonlinearPushoverAnalysis.run_pushover(3, 1, 0.1, 0.001)
    return {"status": res["status"]}

run_problem(51, "Cantilever Plastic Hinge Yielding", problem_51)

# Problem 52: Multi-story Pushover convergence
def problem_52():
    # Simple 2D portal frame logic in 3D model
    ops.wipe(); ops.model('basic','-ndm',3,'-ndf',6)
    ops.node(1,0,0,0); ops.node(2,4,0,0); ops.node(3,0,0,3); ops.node(4,4,0,3)
    ops.fix(1,1,1,1,1,1,1); ops.fix(2,1,1,1,1,1,1)
    ops.geomTransf('Linear', 1, 0, 1, 0)
    ops.element('elasticBeamColumn', 1,1,3, 0.1, 2e8, 8e7, 1e-4, 1e-4, 1e-4, 1)
    ops.element('elasticBeamColumn', 2,2,4, 0.1, 2e8, 8e7, 1e-4, 1e-4, 1e-4, 1)
    ops.element('elasticBeamColumn', 3,3,4, 0.1, 2e8, 8e7, 1e-4, 1e-4, 1e-4, 1)
    
    ops.timeSeries('Linear', 1)
    ops.pattern('Plain', 1, 1)
    ops.load(3, 10.0, 0, 0, 0, 0, 0)
    ops.load(4, 10.0, 0, 0, 0, 0, 0)
    
    res = NonlinearPushoverAnalysis.run_pushover(3, 1, 0.05, 0.001)
    return res

run_problem(52, "Portal Frame Pushover", problem_52)

# Problem 53: Material Deterioration (Bilin)
def problem_53():
    ops.wipe(); ops.model('basic','-ndm',3,'-ndf',6)
    # Testing if Bilin converges under simple cyclic or monotonic
    # Using the module method
    NonlinearPushoverAnalysis.define_imk_hinge_material(1, 1.0e6, 150.0, 0.03, 0.1, 10.0)
    return {"status": "Material defined successfully"}

run_problem(53, "IMK Bilin Material Definition", problem_53)

# Problem 54: High Drift Target (0.5m)
def problem_54():
    # Large displacement on flexible column
    ops.wipe(); ops.model('basic','-ndm',3,'-ndf',6)
    ops.node(1,0,0,0); ops.node(2,0,0,5.0); ops.fix(1,1,1,1,1,1,1)
    ops.geomTransf('Linear',1,0,1,0)
    ops.element('elasticBeamColumn',1,1,2,0.1,2e8,8e7,1e-4,1e-4,1e-4,1)
    ops.timeSeries('Linear', 1)
    ops.pattern('Plain',1,1); ops.load(2,1.0,0,0,0,0,0)
    res = NonlinearPushoverAnalysis.run_pushover(2, 1, 0.5, 0.01)
    return res

run_problem(54, "High Drift Convergence", problem_54)

# Problem 55: Reverse Displacement (Pushover Direction)
def problem_55():
    ops.wipe(); ops.model('basic','-ndm',3,'-ndf',6)
    ops.node(1,0,0,0); ops.node(2,0,0,3.0); ops.fix(1,1,1,1,1,1,1)
    ops.geomTransf('Linear',1,0,1,0)
    ops.element('elasticBeamColumn',1,1,2,0.1,2e8,8e7,1e-4,1e-4,1e-4,1)
    ops.timeSeries('Linear', 1)
    ops.pattern('Plain',1,1); ops.load(2,-1.0,0,0,0,0,0)
    res = NonlinearPushoverAnalysis.run_pushover(2, 1, -0.1, -0.001) 

run_problem(55, "Negative Displacement Pushover", problem_55)
