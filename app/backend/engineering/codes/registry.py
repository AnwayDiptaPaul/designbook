"""Versioned standards metadata and load-factor registry.

Built-in entries are a calculation scaffold, not a claim that every code
provision has been independently reviewed. Each release carries explicit
source and review metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable, Mapping


@dataclass(frozen=True, slots=True)
class CodeReference:
    standard: str
    edition: str
    source_reference: str
    review_status: str = "prototype"


@dataclass(frozen=True, slots=True)
class CombinationDefinition:
    name: str
    category: str
    factors: Mapping[str, float]
    reference: CodeReference

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("combination name cannot be empty")
        if self.category not in {"strength", "serviceability"}:
            raise ValueError(f"unsupported combination category: {self.category}")
        normalized = {str(case): float(factor) for case, factor in self.factors.items()}
        if not normalized:
            raise ValueError("combination must contain at least one load case")
        object.__setattr__(self, "factors", MappingProxyType(normalized))


@dataclass(frozen=True, slots=True)
class CodeRelease:
    reference: CodeReference
    combinations: tuple[CombinationDefinition, ...]

    def combinations_for(self, category: str | None = None) -> tuple[CombinationDefinition, ...]:
        if category is None:
            return self.combinations
        return tuple(item for item in self.combinations if item.category == category)


class CodeRegistry:
    """Explicit registry of releases used by engineering calculations."""

    def __init__(self, releases: Iterable[CodeRelease] = ()) -> None:
        self._releases: dict[tuple[str, str], CodeRelease] = {}
        for release in releases:
            self.register(release)

    def register(self, release: CodeRelease) -> None:
        key = (release.reference.standard, release.reference.edition)
        if key in self._releases:
            raise ValueError(f"code release already registered: {key}")
        self._releases[key] = release

    def get(self, standard: str, edition: str) -> CodeRelease:
        try:
            return self._releases[(standard, edition)]
        except KeyError as exc:
            raise KeyError(f"unsupported code release: {standard} {edition}") from exc

    def releases(self) -> tuple[CodeRelease, ...]:
        return tuple(self._releases.values())


def _release(standard: str, edition: str) -> CodeRelease:
    reference = CodeReference(
        standard=standard,
        edition=edition,
        source_reference=("doc-files/regulations/BNBC_2020/BNBC_2020_Part-6.pdf" if standard == "BNBC" else "external:ACI_318-19 (not present in repository)"),
        review_status="prototype",
    )
    combos = (
        CombinationDefinition("U1", "strength", {"D": 1.4}, reference),
        CombinationDefinition("U2", "strength", {"D": 1.2, "L": 1.6, "R": 0.5}, reference),
        CombinationDefinition("U3", "strength", {"D": 1.2, "L": 1.0, "R": 1.6, "W": 0.5}, reference),
        CombinationDefinition("U4", "strength", {"D": 1.2, "L": 1.0, "R": 0.5, "W": 1.0}, reference),
        CombinationDefinition("U5", "strength", {"D": 0.9, "W": 1.0}, reference),
        CombinationDefinition("U6", "strength", {"D": 1.2, "E": 1.0, "L": 1.0}, reference),
        CombinationDefinition("U7", "strength", {"D": 0.9, "E": 1.0}, reference),
        CombinationDefinition("S1", "serviceability", {"D": 1.0, "L": 1.0}, reference),
        CombinationDefinition("S2", "serviceability", {"D": 1.0, "L": 0.5}, reference),
        CombinationDefinition("S3", "serviceability", {"D": 1.0, "L": 1.0, "W": 1.0}, reference),
        CombinationDefinition("S4", "serviceability", {"D": 1.0, "E": 0.7}, reference),
    )
    return CodeRelease(reference=reference, combinations=combos)


def get_default_registry() -> CodeRegistry:
    """Return an isolated built-in prototype registry."""

    return CodeRegistry((_release("BNBC", "2020"), _release("ACI", "318-19")))
