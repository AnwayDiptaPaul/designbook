# pyre-ignore-all-errors
import math
from backend.api.schemas.design_standards import StaircaseInput, StaircaseForces, StaircaseResult, BeamDesignInput, BeamDesignForces, MaterialProps
from backend.core.design.beam import BeamDesign

class StaircaseDesign:
    """Design routines for Dog-legged staircases."""
    
    @staticmethod
    def design(inputs: StaircaseInput, forces: StaircaseForces) -> StaircaseResult:
        """
        Span = going + landing.
        Calculates waist slab thickness and main flexural reinforcements.
        """
        span = inputs.going + 1.2 # assume 1.2m landing
        
        # Required waist t
        t = span * 1000 / 25.0
        d = t - 20.0 - 6.0 # cover + half bar
        
        # Loading
        dead_waist = (t/1000.0) * 24.0 * math.sqrt(inputs.rise**2 + inputs.tread**2)/inputs.tread
        dead_steps = (inputs.rise/1000.0) / 2.0 * 24.0
        DL = dead_waist + dead_steps + 1.5 # SDL
        
        wu = 1.2 * DL + 1.6 * forces.LL
        
        Mu = wu * span**2 / 8.0
        
        beam_input = BeamDesignInput(
            width=1000.0,
            depth=t,
            cover=20.0,
            material=inputs.material
        )
        beam_forces = BeamDesignForces(Mu=Mu, Vu=0.0)
        res = BeamDesign.design_flexure(beam_input, beam_forces)
        
        return StaircaseResult(
            waist_slab_t_mm=float(t),
            design_load_wu_kPa=float(wu),
            Mu_kNm_m=float(Mu),
            As_req_mm2_m=float(res.As_req_mm2)
        )
