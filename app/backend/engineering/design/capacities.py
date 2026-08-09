"""Transparent prototype capacity providers.

These calculations are elastic-yield references only. They intentionally do
not claim code-compliant buckling, slenderness, resistance factors, or local
limit-state coverage.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite, pi

from .checks import MemberCapacity

@dataclass(frozen=True, slots=True)
class SteelRectangleSection:
    width: float
    depth: float
    yield_strength: float
    standard: str = "prototype-elastic"
    edition: str = "0.1"
    reference: str = "elastic-yield-section-calculator"


def elastic_yield_capacity(section: SteelRectangleSection) -> MemberCapacity:
    values = (section.width, section.depth, section.yield_strength)
    if any(not isfinite(value) for value in values) or any(value <= 0 for value in values):
        raise ValueError("section dimensions and yield strength must be finite and positive")
    area = section.width * section.depth
    section_modulus = section.width * section.depth**2 / 6.0
    return MemberCapacity(
        axial=area * section.yield_strength,
        moment=section_modulus * section.yield_strength,
        standard=section.standard,
        edition=section.edition,
        reference=section.reference,
        review_status="prototype",
    )

def elastic_column_capacity(section: SteelRectangleSection, length: float, effective_length_factor: float = 1.0, elastic_modulus: float = 200_000_000.0) -> MemberCapacity:
    """Return the lesser of gross-yield and Euler compression capacity.

    Units must be consistent with the section dimensions and modulus. This is
    an elastic mechanics reference only; it omits code slenderness curves,
    residual stress, imperfections, and resistance factors.
    """
    if not isfinite(length) or not isfinite(effective_length_factor) or not isfinite(elastic_modulus):
        raise ValueError("column buckling inputs must be finite")
    if length <= 0 or effective_length_factor <= 0 or elastic_modulus <= 0:
        raise ValueError("column buckling inputs must be positive")
    area = section.width * section.depth
    inertia_weak = min(section.width * section.depth**3 / 12.0, section.depth * section.width**3 / 12.0)
    yield_capacity = area * section.yield_strength
    euler_capacity = pi**2 * elastic_modulus * inertia_weak / (effective_length_factor * length)**2
    return MemberCapacity(
        axial=min(yield_capacity, euler_capacity),
        moment=section.width * section.depth**2 / 6.0 * section.yield_strength,
        standard=section.standard,
        edition=section.edition,
        reference=section.reference + ";elastic-euler-buckling",
        review_status="prototype",
    )