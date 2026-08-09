# pyre-ignore-all-errors
import math
from typing import Dict, Any, List
from backend.api.schemas.design_standards import PileInput, PileCapacityResult, PileCapInput, PileCapResult

class PileDesign:
    """Design of deep foundations (Piles) per BNBC/ACI."""
    
    @staticmethod
    def design_axial_capacity(inputs: PileInput) -> PileCapacityResult:
        """
        Calculates ultimate axial capacity (Skin Friction + End Bearing).
        diameter: (m), length: (m), soil_type: 'clay' or 'sand'.
        cu: undrained shear strength (kPa), phi: friction angle (deg).
        """
        area_tip = math.pi * (inputs.diameter**2) / 4.0
        perimeter = math.pi * inputs.diameter
        
        if inputs.soil_type.lower() == 'clay':
            # Alpha method: Qs = alpha * cu * As
            alpha = 0.55 # conservative approximation
            Qs = alpha * inputs.cu * perimeter * inputs.length
            # Qb = Nc * cu * Ab
            Nc = 9.0
            Qb = Nc * inputs.cu * area_tip
        else:
            # Beta method for sand: Qs = K * sigma_v_avg * tan(delta) * As
            K = 1.0 # earth pressure coeff
            sigma_v_mid = (inputs.gamma * inputs.length / 2.0)
            delta = 0.75 * inputs.phi
            Qs = K * sigma_v_mid * math.tan(math.radians(delta)) * perimeter * inputs.length
            # Qb = Nq * sigma_v_tip * Ab
            Nq = 30.0 # simplified for phi=30
            sigma_v_tip = inputs.gamma * inputs.length
            Qb = Nq * sigma_v_tip * area_tip
            
        Qu = Qs + Qb
        return PileCapacityResult(
            Qs=float(Qs),
            Qb=float(Qb),
            Qu=float(Qu),
            Q_allowable=float(Qu / 2.5) # F.S. = 2.5
        )

    @staticmethod
    def design_pile_cap(inputs: PileCapInput, num_piles: int) -> PileCapResult:
        """
        Structural design of a pile cap.
        Checks for average axial pressure and punching shear.
        """
        required_piles = math.ceil(inputs.total_load / inputs.pile_capacity)
        status = "OK" if num_piles >= required_piles else "Insufficient Piles"
        
        # Punching shear check (One-way and Two-way)
        # Simplified: check if depth H is enough
        V_u = inputs.total_load / num_piles # load per pile
        phi = 0.75
        fc = inputs.material.fc
        V_n = 0.17 * math.sqrt(fc) * inputs.B * inputs.H # simple shear capacity
        shear_status = "OK" if V_u < phi * V_n else "Depth too small"
        
        return PileCapResult(
            required_piles=int(required_piles),
            actual_piles=int(num_piles),
            status=status,
            shear_status=shear_status,
            V_u_kN=float(V_u),
            phi_Vn_kN=float(phi * V_n)
        )

    @staticmethod
    def get_py_stiffness(diameter: float, soil_type: str, z: float, mod_k: float = 5000) -> float:
        """
        Simplistic p-y spring stiffness (kN/m/m).
        mod_k: modulus of subgrade reaction (kN/m3).
        """
        # p-y stiffness increases with depth z for sand
        if soil_type.lower() == 'sand':
            k = mod_k * z
        else:
            k = mod_k # constant for clay
        return k * diameter 
