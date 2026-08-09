"""Seismic load calculation per BNBC 2020 Part 6, Chapter 3.

Supports:
- Equivalent Static Force Method (ESFM)
- Response Spectrum Analysis (RSA) — stub for Phase 4
- Time-History Analysis (THA) — stub for Phase 4

References:
- BNBC 2020 Part 6, Chapter 3
- ASCE 7-05 (referenced by BNBC)
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Optional


# ── BNBC Seismic Tables ──────────────────────────────────

# Seismic zone factors Z (BNBC Table 6.2.12)
SEISMIC_ZONE_FACTOR = {
    "I": 0.075,
    "II": 0.15,
    "III": 0.25,
    "IV": 0.36,
}

# Importance factor I (Table 6.2.13)
IMPORTANCE_FACTOR = {
    "residential": 1.0,
    "commercial": 1.0,
    "industrial": 1.25,
    "mixed": 1.0,
    "essential": 1.5,  # hospitals, fire stations
}

# Site coefficient S (Table 6.2.14) based on soil class
SITE_COEFFICIENT = {
    "SA": 0.8,
    "SB": 1.0,
    "SC": 1.15,
    "SD": 1.35,
    "SE": 1.7,
}

# Response modification factor R (Table 6.2.15)
RESPONSE_MODIFICATION_FACTOR = {
    "OMRF": 3.5,   # Ordinary Moment Resisting Frame
    "IMRF": 5.5,   # Intermediate Moment Resisting Frame
    "SMRF": 8.0,   # Special Moment Resisting Frame
}

# Maximum height limits by frame type and seismic zone
HEIGHT_LIMITS_M = {
    "OMRF": {"I": None, "II": 30, "III": None, "IV": None},
    "IMRF": {"I": None, "II": None, "III": 50, "IV": None},
    "SMRF": {"I": None, "II": None, "III": None, "IV": None},
}


@dataclass
class SeismicInput:
    """Inputs for seismic load calculation."""
    seismic_zone: str              # "I", "II", "III", "IV"
    soil_class: str                # "SA" … "SE"
    occupancy: str                 # "residential", "commercial", etc.
    frame_type: str                # "OMRF", "IMRF", "SMRF"
    total_height_m: float          # total building height
    floor_weights_kn: list[float]  # seismic weight (DL + applicable LL) per floor
    floor_elevations_m: list[float]  # cumulative elevation per floor
    fundamental_period_s: Optional[float] = None  # T (if known from modal analysis)


@dataclass
class SeismicStoryForce:
    floor: int
    elevation_m: float
    weight_kn: float
    force_kn: float
    shear_kn: float  # story shear (cumulative from top)


@dataclass
class SeismicResult:
    """Complete ESFM results."""
    Z: float
    I: float
    S: float
    R: float
    T: float  # fundamental period
    Cs: float  # seismic response coefficient
    W: float  # total seismic weight
    base_shear_kn: float
    overturning_moment_knm: float
    story_forces: list[SeismicStoryForce]
    warnings: list[str] = field(default_factory=list)

    @staticmethod
    def calculate_story_drifts(displacements: list[float], elevations: list[float], Cd: float = 5.5) -> list[float]:
        """Calculates inelastic story drifts: drift = Cd * (delta_i - delta_i-1) / h_story"""
        drifts = []
        for i in range(len(displacements)):
            delta_i = displacements[i]
            delta_prev = displacements[i-1] if i > 0 else 0
            h_story = elevations[i] - (elevations[i-1] if i > 0 else 0)
            inelastic_disp = Cd * (delta_i - delta_prev) 
            drifts.append(inelastic_disp / h_story if h_story > 0 else 0)
        return drifts

    @staticmethod
    def calculate_stability_coefficient(P: float, drift_inelastic: float, V: float, h: float, Cd: float = 5.5) -> float:
        """Calculates P-Delta stability coefficient theta = (P * delta_inelastic) / (V * h * Cd)"""
        return (P * drift_inelastic) / (V * h * Cd) if (V * h * Cd) > 0 else 0

    @staticmethod
    def calculate_torsional_amplification(delta_max: float, delta_avg: float) -> float:
        """
        Calculates torsional amplification factor Ax per BNBC 2020.
        Ax = (delta_max / (1.2 * delta_avg))^2, with 1.0 <= Ax <= 3.0
        """
        if delta_avg <= 0: return 1.0
        ax = (delta_max / (1.2 * delta_avg)) ** 2
        return max(1.0, min(3.0, ax))

    @staticmethod
    def combine_modal_responses(responses: list[float], method: str = "SRSS") -> float:
        """Combines modal responses using SRSS or CQC."""
        if method == "SRSS":
            return math.sqrt(sum(r**2 for r in responses))
        return responses[0] # Simplified

    @staticmethod
    def calculate_rsa_base_shear(modal_weights: list[float], modal_accelerations: list[float]) -> float:
        """Calculates base shear from modal analysis: V = sqrt(sum((Wi * Sa_i)^2))"""
        return math.sqrt(sum((w * a)**2 for w, a in zip(modal_weights, modal_accelerations)))


def estimate_fundamental_period(height_m: float, frame_type: str) -> float:
    """Approximate fundamental period per BNBC empirical formula.

    T = C_t × h^(3/4)

    C_t = 0.0731 for RC moment frames
    C_t = 0.0488 for other systems
    """
    if frame_type in ("OMRF", "IMRF", "SMRF"):
        C_t = 0.0731
    else:
        C_t = 0.0488
    return C_t * height_m ** 0.75


def compute_seismic_coefficient(Z: float, I: float, S: float, R: float, T: float) -> float:
    """Compute seismic response coefficient Cs.

    Cs = 1.2 × S / T^(2/3)  but  Cs ≤ 2.5
    and V = (Z × I × Cs / R) × W

    Minimum: Cs ≥ 0.044 × Z × I (per BNBC)
    """
    Cs = 1.2 * S / (T ** (2.0 / 3.0)) if T > 0 else 2.5
    Cs = min(Cs, 2.5)
    Cs = max(Cs, 0.044 * Z * I)
    return Cs


def calculate_seismic_loads(inp: SeismicInput) -> SeismicResult:
    """Full Equivalent Static Force Method per BNBC 2020.

    Steps:
    1. Look up Z, I, S, R
    2. Estimate T (or use provided)
    3. Compute Cs and base shear V
    4. Distribute V vertically using C_vx method
    """
    warnings: list[str] = []

    Z = SEISMIC_ZONE_FACTOR.get(inp.seismic_zone)
    if Z is None:
        raise ValueError(f"Invalid seismic zone: {inp.seismic_zone}")

    I = IMPORTANCE_FACTOR.get(inp.occupancy, 1.0)
    S = SITE_COEFFICIENT.get(inp.soil_class, 1.35)
    R = RESPONSE_MODIFICATION_FACTOR.get(inp.frame_type, 3.5)

    # Height limit check
    limit = HEIGHT_LIMITS_M.get(inp.frame_type, {}).get(inp.seismic_zone)
    if limit and inp.total_height_m > limit:
        warnings.append(
            f"{inp.frame_type} not permitted above {limit}m in Seismic Zone {inp.seismic_zone}"
        )

    # Fundamental period
    T = inp.fundamental_period_s or estimate_fundamental_period(inp.total_height_m, inp.frame_type)

    # Seismic coefficient
    Cs = compute_seismic_coefficient(Z, I, S, R, T)

    # Total seismic weight
    W = sum(inp.floor_weights_kn)

    # Base shear
    V = (Z * I * Cs / R) * W

    # Vertical distribution exponent k
    if T <= 0.5:
        k = 1.0
    elif T >= 2.5:
        k = 2.0
    else:
        k = 1.0 + (T - 0.5) * (2.0 - 1.0) / (2.5 - 0.5)

    # Compute w_i * h_i^k for all floors
    wh_k = [
        w * (h ** k)
        for w, h in zip(inp.floor_weights_kn, inp.floor_elevations_m)
    ]
    sum_wh_k = sum(wh_k) if sum(wh_k) > 0 else 1.0

    # Distribute forces
    story_forces: list[SeismicStoryForce] = []
    cumulative_shear = 0.0
    overturning_moment = 0.0

    for i in range(len(inp.floor_weights_kn)):
        C_vx = wh_k[i] / sum_wh_k
        Fx = C_vx * V

        story_forces.append(SeismicStoryForce(
            floor=i,
            elevation_m=round(inp.floor_elevations_m[i], 2),
            weight_kn=round(inp.floor_weights_kn[i], 2),
            force_kn=round(Fx, 2),
            shear_kn=0.0,  # filled below
        ))
        overturning_moment += Fx * inp.floor_elevations_m[i]

    # Compute story shears (cumulative from top)
    for i in reversed(range(len(story_forces))):
        cumulative_shear += story_forces[i].force_kn
        story_forces[i].shear_kn = round(cumulative_shear, 2)

    return SeismicResult(
        Z=Z,
        I=I,
        S=S,
        R=R,
        T=round(T, 3),
        Cs=round(Cs, 4),
        W=round(W, 2),
        base_shear_kn=round(V, 2),
        overturning_moment_knm=round(overturning_moment, 2),
        story_forces=story_forces,
        warnings=warnings,
    )
