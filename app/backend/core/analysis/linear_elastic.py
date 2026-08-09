# pyre-ignore-all-errors
import openseespy.opensees as ops
from typing import Dict, Any

class LinearElasticAnalysis:
    """Solvers for static linear elastic gravity and lateral lateral sequences."""
    
    @staticmethod
    def run_gravity_analysis(num_steps: int = 10) -> bool:
        """
        Runs a standard gravity load sequence.
        Applies load in increments and returns True if converged.
        """
        # Set up analysis parameters
        ops.system('BandGeneral')
        ops.numberer('RCM')
        ops.constraints('Transformation')
        ops.integrator('LoadControl', 1.0 / num_steps)
        ops.algorithm('Linear')
        ops.analysis('Static')
        
        # Run
        status = ops.analyze(num_steps)
        
        # Maintain constant gravity loads and reset time to zero for subsequent lateral/dynamic steps
        ops.loadConst('-time', 0.0)
        
        return status == 0
        
    @staticmethod
    def run_lateral_push(node_tags: list[int], forces_X: list[float], forces_Y: list[float], num_steps: int = 10) -> bool:
        """
        Runs a static lateral push (e.g. for Wind or Equivalent Static Seismic).
        Assuming gravity has already been run and loadConst applied.
        """
        # Create a new load pattern for lateral forces
        pattern_tag = 2
        ops.pattern('Plain', pattern_tag, 'Linear')
        
        # Apply forces to nodes
        for tag, fx, fy in zip(node_tags, forces_X, forces_Y):
            # args: node_tag, Fx, Fy, Fz, Mx, My, Mz
            ops.load(tag, fx, fy, 0.0, 0.0, 0.0, 0.0)
            
        ops.integrator('LoadControl', 1.0 / num_steps)
        ops.analysis('Static')
        
        status = ops.analyze(num_steps)
        return status == 0
        
    @staticmethod
    def run_eigenvalue_analysis(num_modes: int) -> dict:
        """Runs modal analysis and extracts periods and mode shapes."""
        # Generalized eigenvalue problem
        eigen_values = ops.eigen(num_modes)
        
        periods = []
        frequencies = []
        for w2 in eigen_values:
            import math
            # Calculate angular frequency and period
            if w2 > 0:
                w = math.sqrt(w2)
                t = 2.0 * math.pi / w
                periods.append(t)
                frequencies.append(w)
            else:
                periods.append(0)
                frequencies.append(0)
                
        return {
            "periods": periods,
            "frequencies": frequencies,
            "eigen_values": eigen_values
        }
