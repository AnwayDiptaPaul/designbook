import openseespy.opensees as ops

class GeometricNonlinearity:
    """Handles P-Delta and Large Displacement geometric transformations."""
    
    @staticmethod
    def apply_pdelta_transformation(tag: int, vecxz: list[float] = [0.0, 0.0, 1.0]):
        """
        Defines a P-Delta geometric transformation for 3D elements.
        Includes secondary P-Delta moments but assumes small strains.
        """
        ops.geomTransf('PDelta', tag, *vecxz)
        
    @staticmethod
    def apply_corotational_transformation(tag: int, vecxz: list[float] = [0.0, 0.0, 1.0]):
        """
        Defines a Corotational geometric transformation for 3D elements.
        Exact kinematics for arbitrarily large displacements and rotations.
        """
        ops.geomTransf('Corotational', tag, *vecxz)
        
    @staticmethod
    def check_stability_coefficient(P: float, delta: float, V: float, h: float, Cd: float = 1.0, Ie: float = 1.0) -> float:
        """
        Calculates the stability coefficient theta (theta = P * delta / (V * h))
        Used to determine if P-Delta effects must be included per ASCE 7/BNBC.
        If theta > 0.10, P-Delta is required.
        """
        # Adjusted delta
        delta_inelastic = delta * Cd / Ie
        theta = (P * delta_inelastic) / (V * h)
        return theta
