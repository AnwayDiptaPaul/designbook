"""Modal spectral demand and SRSS combination primitives."""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite, sqrt

from .response_spectrum import evaluate_spectrum

@dataclass(frozen=True, slots=True)
class ModalSpectralResponse:
    modal_demands: tuple[float, ...]
    combined_srss: float


def combine_srss(values: tuple[float, ...]) -> float:
    if not values or any(not isfinite(value) for value in values):
        raise ValueError("SRSS requires at least one finite response")
    return sqrt(sum(value * value for value in values))


def compute_modal_spectral_response(periods: tuple[float, ...], participation_factors: tuple[float, ...], spectrum: tuple[tuple[float, float], ...]) -> ModalSpectralResponse:
    if len(periods) == 0 or len(periods) != len(participation_factors):
        raise ValueError("period and participation dimensions must match and be non-empty")
    if any(not isfinite(period) or period < 0 for period in periods) or any(not isfinite(factor) for factor in participation_factors):
        raise ValueError("modal response inputs must be finite and periods non-negative")
    demands = tuple(factor * evaluate_spectrum(period, spectrum) for period, factor in zip(periods, participation_factors))
    return ModalSpectralResponse(demands, combine_srss(demands))

def combine_cqc(angular_frequencies: tuple[float, ...], responses: tuple[float, ...], *, damping_ratio: float = 0.05) -> float:
    """Combine modal responses using the complete quadratic combination rule."""
    if not angular_frequencies or len(angular_frequencies) != len(responses):
        raise ValueError("CQC frequency and response dimensions must match and be non-empty")
    if any(not isfinite(value) or value <= 0 for value in angular_frequencies) or any(not isfinite(value) for value in responses):
        raise ValueError("CQC frequencies must be positive and responses finite")
    if not isfinite(damping_ratio) or damping_ratio < 0 or damping_ratio >= 1:
        raise ValueError("CQC damping ratio must be finite and in [0, 1)")
    total = 0.0
    for first, omega_i in enumerate(angular_frequencies):
        for second, omega_j in enumerate(angular_frequencies):
            if first == second:
                correlation = 1.0
            else:
                ratio = omega_j / omega_i
                numerator = 8.0 * damping_ratio**2 * (1.0 + ratio) * ratio**1.5
                denominator = (1.0 - ratio**2)**2 + 4.0 * damping_ratio**2 * ratio * (1.0 + ratio)**2
                correlation = numerator / denominator if denominator else 0.0
            total += correlation * responses[first] * responses[second]
    if total < -1e-10:
        raise ValueError("CQC combination produced a negative quadratic value")
    return sqrt(max(total, 0.0))
@dataclass(frozen=True, slots=True)
class DirectionalCombination:
    x_primary: float
    y_primary: float


def combine_orthogonal_directions(response_x: float, response_y: float, *, secondary_factor: float = 0.30) -> DirectionalCombination:
    """Return signed 100%-X+factor-Y and factor-X+100%-Y cases."""
    if any(not isfinite(value) for value in (response_x, response_y, secondary_factor)):
        raise ValueError("directional responses and factor must be finite")
    if secondary_factor < 0 or secondary_factor > 1:
        raise ValueError("secondary directional factor must be in [0, 1]")
    return DirectionalCombination(response_x + secondary_factor * response_y, secondary_factor * response_x + response_y)