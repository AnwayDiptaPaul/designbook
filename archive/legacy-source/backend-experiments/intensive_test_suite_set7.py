import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.analysis.opensees_model import OpenSeesModelBuilder
from core.analysis.pdelta import GeometricNonlinearity
from core.analysis.response_spectrum import ResponseSpectrumAnalysis

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
print("INTENSIVE TEST SUITE - SET 7 (PROBLEMS 31-35)")
print("==================================================")

# Helper to build a simple SDOF cantilever
def build_sdof(L=3000, m=10, E=2.0e5, I=1.0e8, use_pdelta=False):
    ops.wipe()
    ops.model('basic', '-ndm', 3, '-ndf', 6)
    ops.node(1, 0, 0, 0)
    ops.node(2, 0, 0, L)
    ops.fix(1, 1, 1, 1, 1, 1, 1)
    ops.mass(2, m, m, m, 0, 0, 0)
    
    transfTag = 1
    if use_pdelta:
        ops.geomTransf('PDelta', transfTag, 0, 1, 0)
    else:
        ops.geomTransf('Linear', transfTag, 0, 1, 0)
        
    # A=1e5, J=1e8, Iy=I, Iz=I
    ops.element('elasticBeamColumn', 1, 1, 2, 1e5, E, E/2.4, 1e8, I, I, transfTag)

# Problem 31: Natural Period Calculation
def problem_31():
    # SDOF: T = 2*pi*sqrt(m/k)
    # k = 3EI/L^3 = 3 * 2e5 * 1e8 / 3000^3 = 6e13 / 2.7e10 = 2222.2 N/mm = 2.22 kN/m
    # m = 10 ton = 10000 kg. 
    # T = 2*pi*sqrt(10000 / 2222222) = 0.421 s
    build_sdof(m=10.0) # mass in tons? OpenSees mass is just value. 
    # Use N-mm: m = 0.01 (10kg/mm? No, use consistent units).
    # Let's use m = 10000 kg, k = 2222.2 N/mm. NO! 
    # Standard: SI(m, kg, s). L=3, E=2e11, I=1e-4, m=10000. 
    # k = 3 * 2e11 * 1e-4 / 3^3 = 6e7 / 27 = 2.22e6 N/m.
    # T = 2*pi*sqrt(10000 / 2.22e6) = 0.421 s.
    ops.wipe()
    ops.model('basic', '-ndm', 3, '-ndf', 6)
    ops.node(1, 0, 0, 0); ops.node(2, 0, 0, 3.0)
    ops.fix(1, 1, 1, 1, 1, 1, 1)
    ops.mass(2, 10000, 10000, 10000, 0, 0, 0)
    ops.geomTransf('Linear', 1, 0, 1, 0)
    ops.element('elasticBeamColumn', 1, 1, 2, 0.1, 2e11, 8e10, 1e-4, 1e-4, 1e-4, 1)
    
    eigen = ops.eigen(1)
    period = 2 * math.pi / math.sqrt(eigen[0])
    return {"calculated_period_sec": period, "theoretical_target": 0.421}

run_problem(31, "Natural Period (SDOF)", problem_31)

# Problem 32: Base Shear Spectrum
def problem_32():
    spec = ResponseSpectrumAnalysis.generate_design_spectrum(z=0.2, s=1.5, i=1.0, r=5.0)
    # T = 0.5s -> Cs = 1.2 * 1.5 / 0.5^(2/3) = 1.8 / 0.63 = 2.85 -> Cap at 2.5
    # Sa = 0.2 * 1.0 * 2.5 / 5.0 = 0.1g
    T_idx = int(0.5 / 0.05)
    return {"Sa_at_0.5s": spec["accelerations"][T_idx]}

run_problem(32, "BNBC Design Spectrum", problem_32)

# Problem 33: P-Delta Effect
def problem_33():
    # Vertical load P on cantilever
    # Linear: Disp = V*L^3 / 3EI
    # P-Delta: Disp_total = Disp_linear / (1 - P/Pc)
    ops.wipe(); ops.model('basic','-ndm',3,'-ndf',6)
    ops.node(1,0,0,0); ops.node(2,0,0,3.0); ops.fix(1,1,1,1,1,1,1)
    ops.geomTransf('PDelta', 1, 0, 1, 0)
    ops.element('elasticBeamColumn', 1,1,2, 0.1, 2e11, 8e10, 1e-4, 1e-4, 1e-4, 1)
    
    # Gravity PA
    ops.timeSeries('Constant', 1)
    ops.pattern('Plain', 1, 1)
    ops.load(2, 0, 0, -500000, 0, 0, 0) # 500kN axial
    ops.constraints('Transformation'); ops.numberer('RCM'); ops.system('ProfileSPD')
    ops.test('NormDispIncr', 1.0e-12, 10); ops.algorithm('Newton'); ops.integrator('LoadControl', 1.0)
    ops.analysis('Static'); ops.analyze(1)
    
    # Lateral
    ops.pattern('Plain', 2, 1)
    ops.load(2, 10000, 0, 0, 0, 0, 0) # 10kN lateral
    ops.analyze(1)
    
    disp = ops.nodeDisp(2, 1)
    return {"pdelta_disp_m": disp}

run_problem(33, "P-Delta Nonlinear Displacement", problem_33)

# Problem 34: CQC Combination
def problem_34():
    responses = np.array([100.0, 30.0, 10.0])
    freqs = np.array([2*math.pi*2.0, 2*math.pi*5.0, 2*math.pi*10.0])
    cqc = ResponseSpectrumAnalysis.apply_cqc_combination(responses, freqs)
    return {"cqc_result": cqc}

run_problem(34, "CQC Modal Combination", problem_34)

# Problem 35: Stability Coefficient check
def problem_35():
    # P=1000kN, delta=0.02m, V=100kN, h=3m
    theta = GeometricNonlinearity.check_stability_coefficient(1000, 0.02, 100, 3.0, Cd=4.0, Ie=1.0)
    return {"stability_theta": theta, "limit": 0.10}

run_problem(35, "Stability Coefficient (BNBC)", problem_35)
