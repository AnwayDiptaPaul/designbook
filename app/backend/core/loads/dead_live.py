# pyre-ignore-all-errors
"""Dead and live load calculations per BNBC 2020 / ACI 318."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

# ── Unit weights (kN/m³) ─────────────────────────────────
UNIT_WEIGHTS = {
    "reinforced_concrete": 24.0,
    "plain_concrete": 23.0,
    "brick_masonry": 19.0,
    "steel": 78.5,
    "timber": 6.0,
    "water": 9.81,
    "soil_dry": 16.0,
    "soil_saturated": 20.0,
}

# ── Live loads per BNBC Table 8.2 (kPa) ─────────────────
LIVE_LOADS_KPA = {
    "residential_rooms": 1.9,
    "residential_staircase": 3.0,
    "office": 2.4,
    "commercial_retail": 4.8,
    "assembly_fixed_seats": 2.9,
    "assembly_movable_seats": 4.8,
    "hospital_wards": 1.9,
    "hospital_operating": 2.9,
    "industrial_light": 6.0,
    "industrial_heavy": 12.0,
    "storage_light": 6.0,
    "storage_heavy": 12.0,
    "roof_inaccessible": 0.6,
    "roof_accessible": 1.5,
    "parking": 2.4,
    "corridors_first_floor": 4.8,
    "corridors_above_first": 3.8,
    "balconies": 2.9,
}

# ── Typical superimposed dead loads (kPa) ────────────────
SUPERIMPOSED_DEAD_LOADS = {
    "floor_finish_tile": 1.0,
    "floor_finish_marble": 1.2,
    "floor_finish_terrazzo": 0.8,
    "partition_allowance": 1.0,
    "mep_allowance": 0.5,
    "waterproofing": 0.3,
    "plaster_ceiling": 0.5,
}


@dataclass
class DeadLoadResult:
    """Dead load computation results for a structural member."""
    self_weight_kn_per_m: float = 0.0  # for beams/columns (kN/m or kN)
    self_weight_kpa: float = 0.0       # for slabs (kN/m²)
    superimposed_dead_kpa: float = 0.0
    wall_load_kn_per_m: float = 0.0    # line loads on beams
    total_dead_kpa: float = 0.0


def compute_beam_self_weight(width_mm: float, depth_mm: float, unit_weight: float = 24.0) -> float:
    """Beam self-weight in kN/m."""
    b = width_mm / 1000.0
    h = depth_mm / 1000.0
    return b * h * unit_weight


def compute_slab_self_weight(thickness_mm: float, unit_weight: float = 24.0) -> float:
    """Slab self-weight in kPa (kN/m²)."""
    t = thickness_mm / 1000.0
    return t * unit_weight


def compute_column_self_weight(width_mm: float, depth_mm: float, height_mm: float, unit_weight: float = 24.0) -> float:
    """Column self-weight in kN."""
    b = width_mm / 1000.0
    h = depth_mm / 1000.0
    L = height_mm / 1000.0
    return b * h * L * unit_weight


def compute_wall_line_load(
    wall_height_m: float,
    wall_thickness_mm: float = 125.0,
    unit_weight: float = 19.0,
    plaster_both_sides: bool = True,
) -> float:
    """Wall line load on beam in kN/m.

    Includes plaster on both sides if applicable (12mm each side).
    """
    t = wall_thickness_mm / 1000.0
    load = t * wall_height_m * unit_weight

    if plaster_both_sides:
        plaster_thickness = 0.024  # 12mm × 2
        plaster_weight = 20.0     # cement plaster kN/m³
        load += plaster_thickness * wall_height_m * plaster_weight

    return round(load, 2) # type: ignore


def live_load_reduction_factor(
    tributary_area_m2: float,
    influence_area_factor: float = 2.0,
) -> float:
    """Live load reduction factor per BNBC / ASCE 7.

    L = L_0 × (0.25 + 4.57 / √(K_LL × A_T))

    But L ≥ 0.50 × L_0 for members supporting one floor
    and L ≥ 0.40 × L_0 for members supporting two or more floors.
    """
    A_I = influence_area_factor * tributary_area_m2
    if A_I < 37.2:  # No reduction below 37.2 m² (400 ft²)
        return 1.0

    factor = 0.25 + 4.57 / (A_I ** 0.5)
    return max(factor, 0.40)
