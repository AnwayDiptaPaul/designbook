import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.design.pile import PileDesign

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
print("INTENSIVE TEST SUITE - SET 15 (PROBLEMS 71-75)")
print("==================================================")

# Problem 71: Single Pile Axial Capacity (Clay)
def problem_71():
    res = PileDesign.design_axial_capacity(diameter=0.6, length=20.0, soil_type='clay', cu=60.0)
    return res

run_problem(71, "Pile Axial Capacity in Clay", problem_71)

# Problem 72: Lateral Pile Deflection (p-y springs)
def problem_72():
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    # Pile: 0.6m diam, 15m deep
    L = 15.0; d = 0.6; E = 2.5e7; I = math.pi * (d**4) / 64
    num_nodes = 16 # 1m increments
    for i in range(num_nodes):
        ops.node(i+1, 0, -float(i))
    
    ops.geomTransf('Linear', 1)
    for i in range(num_nodes - 1):
        ops.element('elasticBeamColumn', i+1, i+1, i+2, 0.28, E, I, 1)
        
    # Constrain all nodes to be stable in Y and RZ for this X-only test
    for i in range(num_nodes):
        ops.fix(i+1, 0, 1, 1) # Fix Y and RZ
        
    # p-y springs at each node except head
    for i in range(1, num_nodes):
        z = float(i)
        k = PileDesign.get_py_stiffness(d, 'sand', z, mod_k=10000)
        # zeroLength spring base
        ops.node(i+100, 0, -z); ops.fix(i+100, 1, 1, 1)
        ops.uniaxialMaterial('Elastic', i+100, k)
        ops.element('zeroLength', i+100, i+100, i+1, '-mat', i+100, '-dir', 1)
        
    # Apply lateral load at head (node 1)
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1); ops.load(1, 100.0, 0, 0) 
    ops.system('BandGeneral'); ops.numberer('RCM'); ops.constraints('Plain')
    ops.test('NormDispIncr', 1.0e-8, 10); ops.algorithm('Newton')
    ops.analysis('Static'); ops.analyze(1)
    
    disp_head = ops.nodeDisp(1, 1)
    return {"head_deflection_mm": disp_head * 1000}

run_problem(72, "Lateral Pile p-y Response (Sand)", problem_72)

# Problem 74: Pile Cap Capacity
def problem_74():
    res = PileDesign.design_pile_cap(pile_capacity=1000.0, num_piles=4, total_load=3500.0, 
                                     fc=25.0, fy=415.0, B=2000.0, H=800.0)
    return res

run_problem(74, "Pile Cap Verification", problem_74)
