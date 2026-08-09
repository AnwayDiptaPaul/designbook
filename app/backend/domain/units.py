"""Small, deterministic unit boundary for the engineering domain.

All persisted/calculated structural values are SI.  ``Quantity`` is used at
boundaries where a unit must travel with a value; the calculation modules can
continue to use plain floats after validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class UnitSystem(StrEnum):
    SI = "SI"
    IMPERIAL = "IMPERIAL"


_CONVERSIONS: dict[tuple[str, str], float] = {
    ("m", "m"): 1.0,
    ("mm", "mm"): 1.0,
    ("mm", "m"): 0.001,
    ("m", "mm"): 1000.0,
    ("kN", "kN"): 1.0,
    ("N", "kN"): 0.001,
    ("kN", "N"): 1000.0,
    ("kPa", "kPa"): 1.0,
    ("Pa", "kPa"): 0.001,
    ("kPa", "Pa"): 1000.0,
    ("MPa", "MPa"): 1.0,
    ("Pa", "MPa"): 1e-6,
    ("MPa", "Pa"): 1e6,
    ("kN/m", "kN/m"): 1.0,
    ("kN/m²", "kN/m²"): 1.0,
    ("kN·m", "kN·m"): 1.0,
}


@dataclass(frozen=True, slots=True)
class Quantity:
    """A finite numeric value with an explicit engineering unit."""

    value: float
    unit: str

    def __post_init__(self) -> None:
        if not isfinite(float(self.value)):
            raise ValueError("quantity value must be finite")
        if not self.unit or self.unit not in {u for pair in _CONVERSIONS for u in pair}:
            raise ValueError(f"unsupported engineering unit: {self.unit!r}")

    def to(self, target_unit: str) -> "Quantity":
        return Quantity(convert(self.value, self.unit, target_unit), target_unit)


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert a supported scalar without rounding intermediate results."""

    factor = _CONVERSIONS.get((from_unit, to_unit))
    if factor is None:
        raise ValueError(f"unsupported conversion: {from_unit!r} -> {to_unit!r}")
    result = float(value) * factor
    if not isfinite(result):
        raise ValueError("converted quantity is not finite")
    return result


def ensure_positive(value: float, field_name: str) -> float:
    """Validate a strictly positive structural input and return it as float."""

    numeric = float(value)
    if not isfinite(numeric) or numeric <= 0.0:
        raise ValueError(f"{field_name} must be a finite value greater than zero")
    return numeric
