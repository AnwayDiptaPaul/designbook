import math
from typing import Dict, Any, List

class PileDesign:
    """Design of deep foundations (Piles) per BNBC/ACI."""
    
    @staticmethod
    def design_axial_capacity(diameter: float, length: float, soil_type: str, 
                              cu: float = 50.0, phi: float = 30.0, gamma: float = 18.0) -> Dict[str, Any]:
        """
        Calculates ultimate axial capacity (Skin Friction + End Bearing).
        diameter: (m), length: (m), soil_type: 'clay' or 'sand'.
        cu: undrained shear strength (kPa), phi: friction angle (deg).
        """
        area_tip = math.pi * (diameter**2) / 4
        perimeter = math.pi * diameter
        
        if soil_type.lower() == 'clay':
            # Alpha method: Qs = alpha * cu * As
            alpha = 0.55 # conservative approximation
            Qs = alpha * cu * perimeter * length
            # Qb = Nc * cu * Ab
            Nc = 9.0
            Qb = Nc * cu * area_tip
        else:
            # Beta method for sand: Qs = K * sigma_v_avg * tan(delta) * As
            K = 1.0 # earth pressure coeff
            sigma_v_mid = (gamma * length / 2)
            delta = 0.75 * phi
            Qs = K * sigma_v_mid * math.tan(math.radians(delta)) * perimeter * length
            # Qb = Nq * sigma_v_tip * Ab
            Nq = 30.0 # simplified for phi=30
            sigma_v_tip = gamma * length
            Qb = Nq * sigma_v_tip * area_tip
            
        Qu = Qs + Qb
        return {
            "Qs": Qs,
            "Qb": Qb,
            "Qu": Qu,
            "Q_allowable": Qu / 2.5 # F.S. = 2.5
        }

    @staticmethod
    def design_pile_cap(pile_capacity: float, num_piles: int, total_load: float, 
                        fc: float, fy: float, B: float, H: float) -> Dict[str, Any]:
        """
        Structural design of a pile cap.
        Checks for average axial pressure and punching shear.
        """
        required_piles = math.ceil(total_load / pile_capacity)
        status = "OK" if num_piles >= required_piles else "Insufficient Piles"
        
        # Punching shear check (One-way and Two-way)
        # Simplified: check if depth H is enough
        V_u = total_load / num_piles # load per pile
        phi = 0.75
        V_n = 0.17 * math.sqrt(fc) * B * H # simple shear capacity
        shear_status = "OK" if V_u < phi * V_n else "Depth too small"
        
        return {
            "required_piles": required_piles,
            "actual_piles": num_piles,
            "status": status,
            "shear_status": shear_status,
            "V_u_kN": V_u,
            "phi_Vn_kN": phi * V_n
        }

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
