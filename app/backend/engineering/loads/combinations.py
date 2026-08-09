"""Deterministic load-combination evaluation and envelope helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isfinite

from backend.engineering.codes.registry import CodeRelease, CombinationDefinition


def generate_combinations(
    release: CodeRelease,
    category: str | None = None,
    available_cases: Sequence[str] | None = None,
) -> tuple[CombinationDefinition, ...]:
    """Return definitions applicable to a model without inventing load cases.

    Definitions remain visible when a model lacks a case; evaluation raises a
    clear missing-case error instead of treating missing action as zero.
    """

    if category not in {None, "strength", "serviceability"}:
        raise ValueError(f"unsupported combination category: {category}")
    combinations = release.combinations_for(category)
    if available_cases is None:
        return combinations
    known = set(available_cases)
    return tuple(item for item in combinations if set(item.factors).issubset(known))


def combination_value(
    definition: CombinationDefinition,
    case_values: Mapping[str, float],
) -> float:
    """Evaluate one scalar response using a stable factor order."""

    missing = sorted(set(definition.factors) - set(case_values))
    if missing:
        raise KeyError(f"missing load cases for {definition.name}: {', '.join(missing)}")
    total = 0.0
    for case_name in sorted(definition.factors):
        value = float(case_values[case_name])
        factor = float(definition.factors[case_name])
        if not isfinite(value) or not isfinite(factor):
            raise ValueError("load-case values and factors must be finite")
        total += factor * value
    if not isfinite(total):
        raise ValueError("combination result is not finite")
    return total
