# pyre-ignore-all-errors
from __future__ import annotations
from typing import List, Dict, Any


def get_standard_combinations() -> List[Dict[str, Any]]:
    """Return all standard strength and serviceability load combinations."""
    return [
        # ── Strength (Ultimate) ──────────────────────────────
        {
            "name": "U1",
            "combo_type": "strength",
            "factors": {"dead": 1.4},
        },
        {
            "name": "U2",
            "combo_type": "strength",
            "factors": {"dead": 1.2, "live": 1.6},
        },
        {
            "name": "U3a",
            "combo_type": "strength",
            "factors": {"dead": 1.2, "live": 1.0, "wind_x_pos": 0.5},
        },
        {
            "name": "U3b",
            "combo_type": "strength",
            "factors": {"dead": 1.2, "live": 1.0, "wind_x_neg": 0.5},
        },
        {
            "name": "U3c",
            "combo_type": "strength",
            "factors": {"dead": 1.2, "live": 1.0, "wind_y_pos": 0.5},
        },
        {
            "name": "U3d",
            "combo_type": "strength",
            "factors": {"dead": 1.2, "live": 1.0, "wind_y_neg": 0.5},
        },
        {
            "name": "U4a",
            "combo_type": "strength",
            "factors": {"dead": 1.2, "live": 1.0, "wind_x_pos": 1.0},
        },
        {
            "name": "U4b",
            "combo_type": "strength",
            "factors": {"dead": 1.2, "live": 1.0, "wind_x_neg": 1.0},
        },
        {
            "name": "U4c",
            "combo_type": "strength",
            "factors": {"dead": 1.2, "live": 1.0, "wind_y_pos": 1.0},
        },
        {
            "name": "U4d",
            "combo_type": "strength",
            "factors": {"dead": 1.2, "live": 1.0, "wind_y_neg": 1.0},
        },
        {
            "name": "U5a",
            "combo_type": "strength",
            "factors": {"dead": 0.9, "wind_x_pos": 1.0},
        },
        {
            "name": "U5b",
            "combo_type": "strength",
            "factors": {"dead": 0.9, "wind_x_neg": 1.0},
        },
        {
            "name": "U5c",
            "combo_type": "strength",
            "factors": {"dead": 0.9, "wind_y_pos": 1.0},
        },
        {
            "name": "U5d",
            "combo_type": "strength",
            "factors": {"dead": 0.9, "wind_y_neg": 1.0},
        },
        {
            "name": "U6a",
            "combo_type": "strength",
            "factors": {"dead": 1.2, "live": 1.0, "seismic_x": 1.0},
        },
        {
            "name": "U6b",
            "combo_type": "strength",
            "factors": {"dead": 1.2, "live": 1.0, "seismic_y": 1.0},
        },
        {
            "name": "U7a",
            "combo_type": "strength",
            "factors": {"dead": 0.9, "seismic_x": 1.0},
        },
        {
            "name": "U7b",
            "combo_type": "strength",
            "factors": {"dead": 0.9, "seismic_y": 1.0},
        },
        # ── Serviceability ───────────────────────────────────
        {
            "name": "S1",
            "combo_type": "serviceability",
            "factors": {"dead": 1.0, "live": 1.0},
        },
        {
            "name": "S2",
            "combo_type": "serviceability",
            "factors": {"dead": 1.0, "live": 0.5},
        },
        {
            "name": "S3a",
            "combo_type": "serviceability",
            "factors": {"dead": 1.0, "live": 1.0, "wind_x_pos": 1.0},
        },
        {
            "name": "S3b",
            "combo_type": "serviceability",
            "factors": {"dead": 1.0, "live": 1.0, "wind_y_pos": 1.0},
        },
        {
            "name": "S4a",
            "combo_type": "serviceability",
            "factors": {"dead": 1.0, "seismic_x": 0.7},
        },
        {
            "name": "S4b",
            "combo_type": "serviceability",
            "factors": {"dead": 1.0, "seismic_y": 0.7},
        },
    ]


def generate_envelope(
    member_forces_per_combo: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, Any]]:
    """Generate force envelopes across all load combinations.

    Like ETABS 'Envelope' output — finds the critical max/min for each
    force component across all combinations.

    Args:
        member_forces_per_combo: {combo_name: {"M": val, "V": val, "P": val, "T": val}}

    Returns:
        {"M_max": val, "M_min": val, "V_max": val, ...} with the governing combo name.
    """
    components = ["M", "V", "P", "T", "Mx", "My"]
    envelope: dict[str, dict[str, float | str]] = {}

    for comp in components:
        max_val = float("-inf")
        min_val = float("inf")
        max_combo = ""
        min_combo = ""

        for combo_name, forces in member_forces_per_combo.items():
            val = forces.get(comp)
            if val is None:
                continue
            if val > max_val:
                max_val = val
                max_combo = combo_name
            if val < min_val:
                min_val = val
                min_combo = combo_name

        if max_val > float("-inf"):
            envelope[f"{comp}_max"] = {"value": max_val, "combo": max_combo}
            envelope[f"{comp}_min"] = {"value": min_val, "combo": min_combo}

    return envelope

