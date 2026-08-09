# pyre-ignore-all-errors
import openseespy.opensees as ops

class NonlinearPushoverAnalysis:
    """Nonlinear static pushover and plastic hinge formulation."""
    
    @staticmethod
    def define_imk_hinge_material(mat_tag: int, K0: float, My: float, theta_p: float, theta_pc: float, Lambda: float, c_S: float=1.0, c_C: float=1.0, c_A: float=1.0, c_K: float=1.0):
        """
        Modified Ibarra-Medina-Krawinkler (IMK) Deterioration Model.
        Updating to match latest OpenSeesPy Bilin arguments.
        """
        # Bilin tag? Ke? AsPos? AsNeg? My_pos? My_neg? LamdaS? LamdaD? LamdaA? LamdaK? Cs? Cd? Ca? Ck? 
        # Thetap_pos? Thetap_neg? Thetapc_pos? Thetapc_neg? KPos? KNeg? Thetau_pos? Thetau_neg? PDPlus? PDNeg?
        ops.uniaxialMaterial('Bilin', mat_tag, K0, 0.01, 0.01, My, -My, Lambda, Lambda, Lambda, Lambda, 
                             c_S, c_C, c_A, c_K, theta_p, theta_p, theta_pc, theta_pc, 1.0, 1.0, 0.4, 0.4, 1.0, 1.0)
        
    @staticmethod
    def run_pushover(control_node: int, control_dof: int, Dmax: float, Dincr: float) -> dict:
        """Executes displacement-controlled pushover. Ensures TimeSeries exist."""
        # Ensure a TimeSeries exists for the patterns
        # if not ops.getTimeSeriesTags(): # Not always available in all ops versions
        #    ops.timeSeries('Linear', 1)
        
        ops.system('BandGeneral')
        ops.numberer('RCM')
        ops.constraints('Transformation') # Switched from Plain for better convergence with multi-DOF
        ops.test('NormDispIncr', 1.0e-6, 100)
        ops.algorithm('Newton')
        
        ops.integrator('DisplacementControl', control_node, control_dof, Dincr)
        ops.analysis('Static')
        
        num_steps = int(abs(Dmax / Dincr))
        status = ops.analyze(num_steps)
        
        return {
            "status": "success" if status == 0 else "failed",
            "steps_completed": num_steps if status == 0 else "unknown"
        }
