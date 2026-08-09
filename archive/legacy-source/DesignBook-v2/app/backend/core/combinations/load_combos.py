"""Standard load combinations per ACI 318-19 / BNBC 2020."""


def get_standard_combinations() -> list[dict]:
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
