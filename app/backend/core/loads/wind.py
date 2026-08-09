# pyre-ignore-all-errors
"""Wind load calculation module per BNBC 2020 Part 6, Chapter 2.

Implements the complete wind pressure calculation procedure:
  p = q_z × G × C_p − q_i × G_i × C_pi

References:
- BNBC 2020 Part 6, Chapter 2, Section 6.2.4
- ASCE 7-05 (referenced by BNBC)
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Optional


# ── BNBC Table Data ──────────────────────────────────────

# K_z exposure coefficients (Table 6.2.11) for Exposure B, C, D
# Height z (m): K_z values
EXPOSURE_COEFFICIENTS = {
    "B": {
        0: 0.57, 4.6: 0.57, 6.1: 0.62, 7.6: 0.66, 9.1: 0.70,
        12.2: 0.76, 15.2: 0.81, 18.0: 0.85, 21.3: 0.89, 24.4: 0.93,
        27.4: 0.96, 30.5: 0.99, 36.6: 1.04, 42.7: 1.09, 48.8: 1.13,
        54.9: 1.17, 61.0: 1.20, 76.2: 1.28, 91.4: 1.35, 106.7: 1.41,
        121.9: 1.47, 137.2: 1.52, 152.4: 1.56,
    },
    "C": {
        0: 0.85, 4.6: 0.85, 6.1: 0.90, 7.6: 0.94, 9.1: 0.98,
        12.2: 1.04, 15.2: 1.09, 18.0: 1.13, 21.3: 1.17, 24.4: 1.21,
        27.4: 1.24, 30.5: 1.26, 36.6: 1.31, 42.7: 1.36, 48.8: 1.39,
        54.9: 1.43, 61.0: 1.46, 76.2: 1.53, 91.4: 1.59, 106.7: 1.64,
        121.9: 1.69, 137.2: 1.73, 152.4: 1.77,
    },
    "D": {
        0: 1.03, 4.6: 1.03, 6.1: 1.08, 7.6: 1.12, 9.1: 1.16,
        12.2: 1.22, 15.2: 1.27, 18.0: 1.31, 21.3: 1.34, 24.4: 1.38,
        27.4: 1.40, 30.5: 1.43, 36.6: 1.48, 42.7: 1.52, 48.8: 1.55,
        54.9: 1.58, 61.0: 1.61, 76.2: 1.68, 91.4: 1.73, 106.7: 1.78,
        121.9: 1.82, 137.2: 1.86, 152.4: 1.89,
    },
}

# External pressure coefficients C_p (simplified)
EXTERNAL_PRESSURE_COEFF = {
    "windward_wall": 0.8,
    "leeward_wall": -0.5,  # varies with L/B ratio
    "side_wall": -0.7,
    "roof_windward": -0.7,  # varies with slope
    "roof_leeward": -0.5,
}

# Internal pressure coefficients C_pi
INTERNAL_PRESSURE_COEFF = {
    "enclosed": 0.18,
    "partially_enclosed": 0.55,
    "open": 0.0,
}


@dataclass
class WindLoadInput:
    """All inputs needed for wind load calculation."""
    basic_wind_speed_mps: float  # V (m/s)
    exposure_category: str  # "B", "C", "D"
    topographic_factor: float = 1.0  # K_zt
    wind_directionality_factor: float = 0.85  # K_d
    gust_factor: float = 0.85  # G (rigid building)
    enclosure_type: str = "enclosed"  # "enclosed", "partially_enclosed", "open"
    building_width_m: float = 20.0  # B (perpendicular to wind)
    building_depth_m: float = 15.0  # L (parallel to wind)
    floor_elevations_m: list[float] = field(default_factory=list)  # cumulative elevation of each floor
    floor_heights_m: list[float] = field(default_factory=list)  # floor-to-floor heights


@dataclass
class WindStoryForce:
    floor: int
    elevation_m: float
    K_z: float
    q_z_pa: float      # velocity pressure (Pa = N/m²)
    p_net_pa: float     # net design wind pressure (Pa)
    force_kn: float     # story force (kN)


@dataclass
class WindLoadResult:
    """Complete wind load analysis results."""
    base_shear_kn: float
    overturning_moment_knm: float
    story_forces: list[WindStoryForce]
    pressure_profile: list[dict]  # [{z, q_z, p_windward, p_leeward}]


def interpolate_kz(z: float, exposure: str) -> float:
    """Interpolate K_z from BNBC exposure table."""
    table = EXPOSURE_COEFFICIENTS.get(exposure)
    if table is None:
        raise ValueError(f"Invalid exposure category: {exposure}. Use 'B', 'C', or 'D'.")

    heights = sorted(table.keys())
    if z <= heights[0]:
        return table[heights[0]]
    if z >= heights[-1]:
        return table[heights[-1]]

    # Linear interpolation
    for i in range(len(heights) - 1):
        if heights[i] <= z <= heights[i + 1]:
            h1, h2 = heights[i], heights[i + 1]
            k1, k2 = table[h1], table[h2]
            return k1 + (k2 - k1) * (z - h1) / (h2 - h1)

    return table[heights[-1]]


def compute_velocity_pressure(V: float, K_z: float, K_zt: float, K_d: float) -> float:
    """Compute velocity pressure q_z (Pa) = 0.613 × K_z × K_zt × K_d × V²."""
    return 0.613 * K_z * K_zt * K_d * V ** 2


def calculate_wind_loads(inp: WindLoadInput) -> WindLoadResult:
    """Full BNBC wind load calculation procedure.

    Returns story forces, base shear, and overturning moment.
    """
    C_p_windward = EXTERNAL_PRESSURE_COEFF["windward_wall"]
    C_p_leeward = EXTERNAL_PRESSURE_COEFF["leeward_wall"]
    C_pi = INTERNAL_PRESSURE_COEFF.get(inp.enclosure_type, 0.18)
    G = inp.gust_factor

    story_forces: list[WindStoryForce] = []
    pressure_profile: list[dict] = []

    base_shear = 0.0
    overturning_moment = 0.0

    for i, elev in enumerate(inp.floor_elevations_m):
        K_z = interpolate_kz(elev, inp.exposure_category)
        q_z = compute_velocity_pressure(inp.basic_wind_speed_mps, K_z, inp.topographic_factor, inp.wind_directionality_factor)

        # Windward pressure (positive, pushing)
        p_windward = q_z * G * C_p_windward

        # Leeward pressure (use mean roof height q_h → simplified: use q_z at roof)
        # For simplicity in Phase 1, use q_z at current level for leeward
        p_leeward = q_z * G * C_p_leeward  # negative (suction)

        # Internal pressure
        p_internal = q_z * G * C_pi  # ± (use positive for conservative)

        # Net wind pressure on windward face
        p_net = (p_windward - p_leeward)  # Pa (simplified: no internal offset for MWFRS)

        # Tributary height for this floor
        if i < len(inp.floor_heights_m):
            trib_height = inp.floor_heights_m[i]
        elif inp.floor_heights_m:
            trib_height = inp.floor_heights_m[-1]
        else:
            trib_height = 3.0  # default 3m

        # Story force = p_net × tributary_width × tributary_height
        force_n = p_net * inp.building_width_m * trib_height
        force_kn = force_n / 1000.0

        story_forces.append(WindStoryForce(
            floor=i,
            elevation_m=elev,
            K_z=round(K_z, 4), # type: ignore
            q_z_pa=round(q_z, 2), # type: ignore
            p_net_pa=round(p_net, 2), # type: ignore
            force_kn=round(force_kn, 2), # type: ignore
        ))

        pressure_profile.append({
            "z_m": round(elev, 2), # type: ignore
            "K_z": round(K_z, 4), # type: ignore
            "q_z_pa": round(q_z, 2), # type: ignore
            "p_windward_pa": round(p_windward, 2), # type: ignore
            "p_leeward_pa": round(p_leeward, 2), # type: ignore
            "p_net_pa": round(p_net, 2), # type: ignore
        })

        base_shear += force_kn
        overturning_moment += force_kn * elev

    return WindLoadResult(
        base_shear_kn=round(base_shear, 2), # type: ignore
        overturning_moment_knm=round(overturning_moment, 2), # type: ignore
        story_forces=story_forces,
        pressure_profile=pressure_profile,
    )
