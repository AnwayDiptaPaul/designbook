"""Modal participation and deterministic response-spectrum primitives."""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True, slots=True)
class ParticipationResult:
    factors: tuple[float, ...]
    effective_masses: tuple[float, ...]
    cumulative_effective_mass: float


def modal_participation(masses: tuple[float, ...], mode_shapes: tuple[tuple[float, ...], ...], influence: tuple[float, ...]) -> ParticipationResult:
    size = len(masses)
    if size == 0 or len(influence) != size or any(len(shape) != size for shape in mode_shapes):
        raise ValueError("mass, influence, and mode-shape dimensions must agree")
    if any(not isfinite(value) or value <= 0 for value in masses):
        raise ValueError("masses must be finite and positive")
    if any(not isfinite(value) for value in influence) or any(not isfinite(value) for shape in mode_shapes for value in shape):
        raise ValueError("participation inputs must be finite")
    factors = tuple(sum(masses[index] * shape[index] * influence[index] for index in range(size)) for shape in mode_shapes)
    effective = tuple(value * value for value in factors)
    return ParticipationResult(factors, effective, sum(effective))


def evaluate_spectrum(period: float, points: tuple[tuple[float, float], ...]) -> float:
    if not isfinite(period) or period < 0 or len(points) == 0:
        raise ValueError("period must be finite and non-negative with at least one spectrum point")
    if any(not isfinite(item) or item < 0 for point in points for item in point):
        raise ValueError("spectrum points must be finite and non-negative")
    ordered = tuple(sorted(points, key=lambda point: point[0]))
    if len({point[0] for point in ordered}) != len(ordered):
        raise ValueError("spectrum periods must be unique")
    if period <= ordered[0][0]:
        return ordered[0][1]
    if period >= ordered[-1][0]:
        return ordered[-1][1]
    for (left_period, left_accel), (right_period, right_accel) in zip(ordered, ordered[1:]):
        if left_period <= period <= right_period:
            ratio = (period - left_period) / (right_period - left_period)
            return left_accel + ratio * (right_accel - left_accel)
    raise RuntimeError("spectrum interpolation interval not found")