"""Transparent prototype member design checks.

Capacities are supplied by a reviewed code-specific design module. This layer
only evaluates the declared interaction equation and preserves provenance.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from typing import Literal, Mapping

@dataclass(frozen=True, slots=True)
class MemberDemand:
    axial: float
    moment: float

@dataclass(frozen=True, slots=True)
class MemberCapacity:
    axial: float
    moment: float
    standard: str
    edition: str
    reference: str
    review_status: str = "prototype"

@dataclass(frozen=True, slots=True)
class DesignCheckResult:
    utilization: float
    status: Literal["pass", "fail"]
    demand: MemberDemand
    capacity: MemberCapacity
    equation: str = "|N|/Pn + |M|/Mn"


def check_axial_flexure(demand: MemberDemand, capacity: MemberCapacity) -> DesignCheckResult:
    values = (demand.axial, demand.moment, capacity.axial, capacity.moment)
    if any(not isfinite(value) for value in values):
        raise ValueError("demand and capacity values must be finite")
    if capacity.axial <= 0 or capacity.moment <= 0:
        raise ValueError("capacities must be positive")
    if not capacity.standard.strip() or not capacity.edition.strip() or not capacity.reference.strip():
        raise ValueError("design provenance must be complete")
    utilization = abs(demand.axial) / capacity.axial + abs(demand.moment) / capacity.moment
    return DesignCheckResult(
        utilization=utilization,
        status="pass" if utilization <= 1.0 else "fail",
        demand=demand,
        capacity=capacity,
    )
@dataclass(frozen=True, slots=True)
class GoverningDesignResult:
    combination: str
    check: DesignCheckResult
    checks: Mapping[str, DesignCheckResult]


def check_governing_axial_flexure(demands_by_combination: Mapping[str, MemberDemand], capacity: MemberCapacity) -> GoverningDesignResult:
    if not demands_by_combination:
        raise ValueError("at least one combination demand is required")
    if any(not name.strip() for name in demands_by_combination):
        raise ValueError("combination names cannot be blank")
    checks = {name: check_axial_flexure(demand, capacity) for name, demand in demands_by_combination.items()}
    governing = min(checks, key=lambda name: (-checks[name].utilization, name))
    return GoverningDesignResult(combination=governing, check=checks[governing], checks=checks)