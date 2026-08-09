import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.analysis.opensees_model import OpenSeesModelBuilder
from core.analysis.pdelta import GeometricNonlinearity

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
print("INTENSIVE TEST SUITE - SET 14 (PROBLEMS 66-70)")
print("==================================================")

# Problem 66: Slender Column near Euler Load
def problem_66():
    # P_cr = pi^2 * EI / L^2
    # L=5m, E=2.5e7 kPa, I=0.001 m4
    # P_cr = 3.14^2 * 2.5e10 * 0.001 / 25 = 9.86e6 / 25 = 394.7 kN
    # Application of 350 kN (88% of P_cr)
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    ops.node(1,0,0); ops.node(2,0,5.0); ops.fix(1,1,1,1)
    ops.geomTransf('PDelta', 1)
    ops.element('elasticBeamColumn', 1, 1, 2, 0.1, 2.5e10, 1.0e-3, 1)
    
    # Static analyze
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1); ops.load(2, 0, -350000, 0)
    ops.system('BandGeneral'); ops.numberer('RCM'); ops.constraints('Plain')
    ops.test('NormDispIncr', 1e-12, 10); ops.algorithm('Newton')
    ops.analysis('Static'); ops.analyze(1)
    
    # Lateral load to trigger instability
    ops.pattern('Plain', 2, 1); ops.load(2, 1000, 0, 0) # 1kN lat
    ops.analyze(1)
    
    disp = ops.nodeDisp(2, 1)
    # Theoretical amplification: delta_0 / (1 - P/Pcr)
    # delta_0 = HL^3/3EI = 1000*125 / (3 * 2.5e7) = 125000 / 7.5e7 = 0.00166m
    # delta_pdelta = 0.00166 / (1 - 350/394) = 0.00166 / 0.11 = 0.015m
    return {"pdelta_disp": disp, "theoretical_pdelta": 0.015}

run_problem(66, "Slender Column P-Delta Amplification", problem_66)

# Problem 67: Corotational vs P-Delta (Large Displacement)
def problem_67():
    # Comparing disp for massive rotation
    def run_transf(trans_type):
        ops.wipe(); ops.model('basic','-ndm',2,'-ndf',3)
        ops.node(1,0,0); ops.node(2,10.0,0); ops.fix(1,1,1,1)
        ops.geomTransf(trans_type, 1)
        ops.element('elasticBeamColumn', 1,1,2, 0.1, 2e11, 1e-5, 1)
        ops.timeSeries('Linear', 1); ops.pattern('Plain', 1, 1); ops.load(2, 0, 1e6, 0)
        ops.constraints('Transformation'); ops.numberer('RCM'); ops.system('BandGeneral')
        ops.test('NormDispIncr', 1.0e-6, 40); ops.algorithm('KrylovNewton')
        ops.integrator('DisplacementControl', 2, 2, 0.05) # Smaller steps
        ops.analysis('Static'); ops.analyze(40) # Push to 2m displacement
        return ops.nodeDisp(2, 1) # Axial shortening due to rotation

    x_pdelta = run_transf('PDelta')
    x_corot = run_transf('Corotational')
    return {"pdelta_shortening": x_pdelta, "corot_shortening": x_corot}

run_problem(67, "Corotational vs P-Delta Displacement", problem_67)

# Problem 69: Column with Initial Imperfection
def problem_69():
    # Column offset by 20mm (L=4m)
    ops.wipe(); ops.model('basic','-ndm',2,'-ndf',3)
    ops.node(1,0,0); ops.node(2,0.02,4.0); ops.fix(1,1,1,1)
    ops.geomTransf('PDelta', 1)
    ops.element('elasticBeamColumn', 1,1,2, 0.1, 2e11, 1e-4, 1)
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1); ops.load(2, 0, -500000, 0) # 500kN
    ops.analysis('Static'); ops.analyze(1)
    
    moment_at_base = -ops.nodeReaction(1, 3) if ops.reactions() is None else 0
    ops.reactions()
    moment_at_base = -ops.nodeReaction(1, 3)
    return {"initial_moment": 500*0.02, "pdelta_moment": moment_at_base/1000.0}

run_problem(69, "Column Initial Imperfection Analysis", problem_69)
