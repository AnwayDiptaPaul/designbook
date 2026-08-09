import sys
import os
import math
import numpy as np
import openseespy.opensees as ops

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.analysis.time_history import TimeHistoryAnalysis

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
print("INTENSIVE TEST SUITE - SET 12 (PROBLEMS 56-60)")
print("==================================================")

# Problem 56: Resonance of SDOF
def problem_56():
    ops.wipe(); ops.model('basic','-ndm',3,'-ndf',6)
    ops.node(1,0,0,0); ops.node(2,0,0,3.0); ops.fix(1,1,1,1,1,1,1)
    # k = 1000 N/m, m = 1000 kg => w = sqrt(k/m) = 1. T = 2*pi = 6.28s
    # Use SI units: L=3, E=2e11, I=1e-5. k = 3EI/L^3 = 6e6 / 27 = 2.22e5 N/m
    # m = 2.22e5 kg => w=1 rad/s (f=0.159 Hz)
    m = 222222.0
    ops.mass(2, m, m, m, 0, 0, 0)
    ops.geomTransf('Linear', 1, 0, 1, 0)
    ops.element('elasticBeamColumn', 1, 1, 2, 0.1, 2e11, 8e10, 1e-5, 1e-5, 1e-5, 1)
    
    # Ground motion at resonance (w=1 rad/s)
    ops.timeSeries('Trig', 1, 0.0, 100.0, 6.28, '-factor', 0.1) # 0.1 m/s^2 sine wave
    ops.pattern('UniformExcitation', 1, 1, '-accel', 1)
    
    gamma, beta = TimeHistoryAnalysis.get_newmark_parameters()
    ops.constraints('Transformation'); ops.numberer('RCM'); ops.system('BandGeneral')
    ops.test('NormDispIncr', 1.0e-8, 10); ops.algorithm('Newton')
    ops.integrator('Newmark', gamma, beta)
    ops.analysis('Transient')
    
    ops.analyze(500, 0.1) # 50s
    disp = ops.nodeDisp(2, 1)
    return {"status": "success", "disp_at_resonance": disp}

run_problem(56, "SDOF Resonance check", problem_56)

# Problem 58: Rayleigh Damping implementation
def problem_58():
    ops.wipe(); ops.model('basic','-ndm',3,'-ndf',6)
    ops.node(1,0,0,0); ops.node(2,0,0,3.0); ops.fix(1,1,1,1,1,1,1)
    ops.mass(2, 10000, 10000, 10000, 0, 0, 0)
    ops.geomTransf('Linear', 1, 0, 1, 0)
    ops.element('elasticBeamColumn', 1, 1, 2, 0.1, 2e11, 8e10, 1e-4, 1e-4, 1e-4, 1)
    
    # Eigen analysis to get frequencies
    w2 = ops.eigen(1)
    w = math.sqrt(w2[0])
    
    # Apply 5% Rayleigh damping at mode 1
    # zeta = 0.5 * (alpha/w + beta*w)
    # let alpha = 0, beta = 2*zeta/w
    zeta = 0.05
    beta_rayleigh = 2 * zeta / w
    ops.rayleigh(0.0, 0.0, beta_rayleigh, 0.0)
    
    return {"alpha": 0.0, "beta": beta_rayleigh, "mode1_w": w}

run_problem(58, "Rayleigh Damping Coefficients", problem_58)

# Problem 59: Multi-story Impulse
def problem_59():
    ops.wipe(); ops.model('basic','-ndm',3,'-ndf',6)
    # 2-story
    ops.node(1,0,0,0); ops.node(2,0,0,3); ops.node(3,0,0,6)
    ops.fix(1,1,1,1,1,1,1)
    ops.mass(2, 1000, 1000, 1000, 0, 0, 0); ops.mass(3, 1000, 1000, 1000, 0, 0, 0)
    ops.geomTransf('Linear', 1, 0, 1, 0)
    ops.element('elasticBeamColumn', 1,1,2, 0.1, 2e11, 8e10, 1e-4, 1e-4, 1e-4, 1)
    ops.element('elasticBeamColumn', 2,2,3, 0.1, 2e11, 8e10, 1e-4, 1e-4, 1e-4, 1)
    
    # Impulse at t=0.0 to 0.1s
    ops.timeSeries('Path', 1, '-dt', 0.1, '-values', 1000.0, 0.0, 0.0) # 1000N hit
    ops.pattern('Plain', 1, 1)
    ops.load(3, 1.0, 0, 0, 0, 0, 0)
    
    ops.constraints('Transformation'); ops.numberer('RCM'); ops.system('BandGeneral')
    ops.integrator('Newmark', 0.5, 0.25)
    ops.analysis('Transient')
    ops.analyze(100, 0.01)
    
    return {"status": "success", "roof_disp": ops.nodeDisp(3, 1)}

run_problem(59, "2-story Impulse Response", problem_59)

# Problem 60: Damped Free Vibration decay
def problem_60():
    # Push and release with damping
    ops.wipe(); ops.model('basic','-ndm',3,'-ndf',6)
    ops.node(1,0,0,0); ops.node(2,0,0,3.0); ops.fix(1,1,1,1,1,1,1)
    ops.mass(2, 1000, 1000, 1000, 0, 0, 0)
    ops.geomTransf('Linear', 1, 0, 1, 0)
    ops.element('elasticBeamColumn', 1, 1, 2, 0.1, 2e11, 8e10, 1e-4, 1e-4, 1e-4, 1)
    
    # Initial displacement
    ops.timeSeries('Constant', 1)
    ops.pattern('Plain', 1, 1)
    ops.load(2, 1000.0, 0, 0, 0, 0, 0)
    ops.algorithm('Newton')
    ops.integrator('LoadControl', 1.0); ops.analysis('Static'); ops.analyze(1)
    ops.reactions(); ops.loadConst()
    
    w2 = ops.eigen(1); w = math.sqrt(w2[0])
    ops.rayleigh(0, 0, 2*0.1/w, 0) # 10% damping
    
    ops.integrator('Newmark', 0.5, 0.25); ops.analysis('Transient')
    ops.analyze(200, 0.01)
    
    disp = ops.nodeDisp(2, 1)
    return {"decayed_disp": disp}

run_problem(60, "Damped Free Vibration decay", problem_60)
