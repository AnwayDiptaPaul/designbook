import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.design.footing_combined import CombinedFootingDesign
from core.soil.soil_reaction import SoilMechanics

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
print("INTENSIVE TEST SUITE - SET 17 (PROBLEMS 81-85)")
print("==================================================")

# Problem 81: Combined Footing Geometry
def problem_81():
    # P1=1000, P2=1500, c_c=4, q_allow=200
    res = CombinedFootingDesign.design(1000.0, 1500.0, 4.0, 200.0, 25.0, 415.0)
    # x_bar = 1500*4 / 2500 = 2.4m from P1.
    # L = 2 * (2.4 + 0.2) = 5.2m.
    # B = 2500 / (5.2 * 200) = 2500 / 1040 = 2.4m.
    return res

run_problem(81, "Combined Footing Centroid", problem_81)

# Problem 82: Winkler Spring Stiffness
def problem_82():
    ks = SoilMechanics.calculate_winkler_spring_stiffness(200.0)
    # 200 * 3 / 0.025 = 24000
    return {"ks_kn_m3": ks}

run_problem(82, "Winkler Ks calculation", problem_82)

# Problem 83: Foundation Settlement on Springs
def problem_83():
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    # Footing: 5m x 2m. ks = 24000. 
    # Center node 1 at (0,0). Spring area = 5*2 = 10m2.
    # Total k = 24000 * 10 = 240000 kN/m.
    ops.node(1, 0, 0); ops.node(2, 0, 0); ops.fix(1, 1, 1, 1)
    ops.fix(2, 1, 0, 1) # Stable in X and RZ
    ops.uniaxialMaterial('Elastic', 1, 240000.0)
    ops.element('zeroLength', 1, 1, 2, '-mat', 1, '-dir', 2) # Y direction
    
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1); ops.load(2, 0, -2000.0, 0) # 2000kN load
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral')
    ops.test('NormDispIncr', 1.0e-8, 10); ops.algorithm('Newton')
    ops.analysis('Static'); ops.analyze(1)
    
    settlement = ops.nodeDisp(2, 2)
    # Should be 2000 / 240000 = 0.00833m = 8.33mm.
    return {"settlement_mm": settlement * 1000}

run_problem(83, "Settlement under Point Load", problem_83)

# Problem 84: Non-linear Soil (No Tension)
def problem_84():
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    ops.node(1, 0, 0); ops.node(2, 0, 0); ops.fix(1, 1, 1, 1)
    ops.fix(2, 1, 0, 1)
    # Elastic-No Tension (ENT)
    ops.uniaxialMaterial('ENT', 1, 10000.0)
    ops.element('zeroLength', 1, 1, 2, '-mat', 1, '-dir', 2)
    
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1); ops.load(2, 0, 50.0, 0) # Tension
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral')
    ops.test('NormDispIncr', 1.0e-8, 10); ops.algorithm('Newton')
    ops.analysis('Static'); ops.analyze(1)
    
    force = ops.nodeReaction(1, 2) if ops.reactions() is None else 0
    ops.reactions()
    force = ops.nodeReaction(1, 2) 
    return {"tension_force": force}

run_problem(84, "Compression-Only Soil Logic", problem_84)
