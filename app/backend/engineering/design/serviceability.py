"""Auditable serviceability limit-state checks."""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from typing import Literal, Mapping

@dataclass(frozen=True, slots=True)
class ServiceabilityCheckResult:
    demand: float
    limit: float
    utilization: float
    status: Literal["pass", "fail"]
    criterion: str
    reference: str


def check_deflection(deflection: float, span: float, limit_ratio: float, *, reference: str = "prototype-serviceability") -> ServiceabilityCheckResult:
    if any(not isfinite(value) for value in (deflection, span, limit_ratio)) or span <= 0 or limit_ratio <= 0:
        raise ValueError("deflection inputs must be finite and positive where applicable")
    if not reference.strip():
        raise ValueError("serviceability reference cannot be blank")
    limit = span / limit_ratio
    utilization = abs(deflection) / limit
    return ServiceabilityCheckResult(abs(deflection), limit, utilization, "pass" if utilization <= 1.0 else "fail", f"L/{limit_ratio:g} deflection", reference)


def check_story_drift(relative_displacement: float, story_height: float, drift_ratio: float, *, reference: str = "prototype-serviceability") -> ServiceabilityCheckResult:
    if any(not isfinite(value) for value in (relative_displacement, story_height, drift_ratio)) or story_height <= 0 or drift_ratio <= 0:
        raise ValueError("drift inputs must be finite and positive where applicable")
    if not reference.strip():
        raise ValueError("serviceability reference cannot be blank")
    limit = story_height * drift_ratio
    utilization = abs(relative_displacement) / limit
    return ServiceabilityCheckResult(abs(relative_displacement), limit, utilization, "pass" if utilization <= 1.0 else "fail", f"story drift <= {drift_ratio:g}h", reference)
@dataclass(frozen=True, slots=True)
class GoverningServiceabilityResult:
    combination: str
    check: ServiceabilityCheckResult
    checks: Mapping[str, ServiceabilityCheckResult]


def _governing(checks: Mapping[str, ServiceabilityCheckResult]) -> GoverningServiceabilityResult:
    if not checks:
        raise ValueError("at least one serviceability combination is required")
    if any(not name.strip() for name in checks):
        raise ValueError("combination names cannot be blank")
    governing = min(checks, key=lambda name: (-checks[name].utilization, name))
    return GoverningServiceabilityResult(governing, checks[governing], checks)


def check_governing_deflection(deflections_by_combination: Mapping[str, float], span: float, limit_ratio: float, *, reference: str = "prototype-serviceability") -> GoverningServiceabilityResult:
    return _governing({name: check_deflection(value, span, limit_ratio, reference=reference) for name, value in deflections_by_combination.items()})


def check_governing_story_drift(drifts_by_combination: Mapping[str, float], story_height: float, drift_ratio: float, *, reference: str = "prototype-serviceability") -> GoverningServiceabilityResult:
    return _governing({name: check_story_drift(value, story_height, drift_ratio, reference=reference) for name, value in drifts_by_combination.items()})