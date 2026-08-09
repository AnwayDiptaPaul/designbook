# pyre-ignore-all-errors
from typing import List, Dict, Any
import numpy as np

class ResponseSpectrumAnalysis:
    """Modal and Response Spectrum Analysis module for OpenSeesPy."""
    
    @staticmethod
    def generate_design_spectrum(z: float, s: float, i: float, r: float, t_max: float = 4.0, dt: float = 0.05) -> Dict[str, List[float]]:
        """
        Generates the BNBC 2020 design response spectrum curve.
        Returns mapped dict of periods (T) and spectral accelerations (Sa).
        """
        # BNBC equations for response spectrum:
        # C_s = 1.2 * S / T^(2/3) <= 2.5
        periods = np.arange(0.01, t_max + dt, dt).tolist()
        accelerations = []
        
        for T in periods:
            Cs = min(1.2 * s / (T**(2/3)), 2.5)
            # Sa = Z * I * Cs / R (normalized by g)
            Sa = (z * i * Cs) / r
            accelerations.append(Sa)
            
        return {
            "periods": periods,
            "accelerations": accelerations
        }
        
    @staticmethod
    def apply_cqc_combination(modal_responses: np.ndarray, modal_frequencies: np.ndarray, damping_ratio: float = 0.05) -> float:
        """
        Applies Complete Quadratic Combination (CQC) method to combine modal responses.
        modal_responses: array of peak responses for each mode
        modal_frequencies: array of frequencies (omega) for each mode
        """
        n_modes = len(modal_responses)
        response_squared = 0.0
        
        for i in range(n_modes):
            for j in range(n_modes):
                r = modal_frequencies[j] / modal_frequencies[i] if modal_frequencies[i] > 0 else 0
                rho_ij = (8 * damping_ratio**2 * (1 + r) * r**1.5) / ((1 - r**2)**2 + 4 * damping_ratio**2 * r * (1 + r)**2) # type: ignore
                response_squared += rho_ij * modal_responses[i] * modal_responses[j] # type: ignore
                
        return np.sqrt(response_squared)
