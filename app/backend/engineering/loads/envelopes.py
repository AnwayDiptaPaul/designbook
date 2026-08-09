"""Governing demand envelopes with explicit combination provenance."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from .combinations import combination_value
from backend.engineering.codes.registry import CombinationDefinition


@dataclass(frozen=True, slots=True)
class EnvelopeValue:
    minimum: float
    minimum_combination: str
    maximum: float
    maximum_combination: str


def evaluate_envelope(
    combinations: tuple[CombinationDefinition, ...],
    responses_by_case: Mapping[str, Mapping[str, float]],
) -> dict[str, EnvelopeValue]:
    """Evaluate each response across combinations and retain governing names."""

    if not combinations:
        raise ValueError("at least one combination is required")
    if not responses_by_case:
        raise ValueError("at least one response is required")

    output: dict[str, EnvelopeValue] = {}
    for response_name, case_values in responses_by_case.items():
        evaluated = [
            (definition.name, combination_value(definition, case_values))
            for definition in combinations
        ]
        minimum_value = min(value for _, value in evaluated)
        maximum_value = max(value for _, value in evaluated)
        minimum_name = min(name for name, value in evaluated if value == minimum_value)
        maximum_name = min(name for name, value in evaluated if value == maximum_value)
        if not isfinite(minimum_value) or not isfinite(maximum_value):
            raise ValueError(f"non-finite envelope for response {response_name}")
        output[response_name] = EnvelopeValue(
            minimum=minimum_value,
            minimum_combination=minimum_name,
            maximum=maximum_value,
            maximum_combination=maximum_name,
        )
    return output