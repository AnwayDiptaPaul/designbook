# pyre-ignore-all-errors
import math

class LiquidTankDesign:
    """Design routines for liquid-retaining structures per ACI 350."""
    
    @staticmethod
    def calculate_hydrostatic_pressure(h: float, gamma_l: float = 9.81) -> float:
        """p = gamma_l * h (kPa). h is depth in meters."""
        return gamma_l * h

    @staticmethod
    def calculate_buoyancy_factor(W_structure: float, V_displaced: float, gamma_w: float = 9.81) -> float:
        """FOS_buoyancy = Weight / Uplift."""
        uplift = V_displaced * gamma_w
        return W_structure / uplift if uplift > 0 else 999

    @staticmethod
    def design_circular_tank_wall(radius: float, h: float, gamma_l: float, fy: float) -> dict:
        """
        Calculates hoop tension T = p * R.
        Then As_hoop = T / (phi * fy * S), where S is serviceability factor (ACI 350).
        """
        p_base = gamma_l * h
        T_max = p_base * radius # kN/m
        
        # ACI 350 durability factor S (typically 0.85 to 1.0)
        S = 0.9 # common for hoop tension
        phi = 0.9
        
        As_req = (T_max * 1000) / (phi * S * fy)
        return {
            "hoop_tension_kN_m": T_max,
            "As_hoop_req_mm2_m": As_req,
            "status": "OK"
        }

    @staticmethod
    def design_tank_flexure(Mu: float, b: float, d: float, fc: float, fy: float) -> dict:
        """
        Flexural design for liquid tanks using ACI 350 S-factor.
        Standard Mu is multiplied by 1.3 or similar durabilty factor.
        """
        S = 1.3 # Flexural durability factor for liquid-tightness
        Mu_durability = Mu * S
        
        from backend.core.design.beam import BeamDesign
        from backend.api.schemas.design_standards import BeamDesignInput, BeamDesignForces, MaterialProps
        b_input = BeamDesignInput(width=b, depth=d+40.0, cover=40.0, material=MaterialProps(fc=fc, fy=fy, fy_v=fy))
        b_forces = BeamDesignForces(Mu=Mu_durability, Vu=0.0)
        res = BeamDesign.design_flexure(b_input, b_forces)
        return {"status": res.status, "As_req_mm2": res.As_req_mm2}
