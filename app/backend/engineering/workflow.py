"""Reference analysis-to-design workflow for linear 2D frames."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping

from .frame_solver import FrameElement2D, FrameNode2D, LinearFrameResult, solve_linear_frame
from .design.checks import DesignCheckResult, MemberCapacity, MemberDemand, GoverningDesignResult, check_governing_axial_flexure

@dataclass(frozen=True, slots=True)
class FrameDesignWorkflowResult:
    analyses_by_combination: Mapping[str, LinearFrameResult]
    demands_by_member: Mapping[int, Mapping[str, MemberDemand]]
    checks_by_member: Mapping[int, GoverningDesignResult]


def run_frame_design_workflow(
    nodes: tuple[FrameNode2D, ...],
    elements: tuple[FrameElement2D, ...],
    loads_by_combination: Mapping[str, Mapping[int, tuple[float, float, float]]],
    capacities_by_member: Mapping[int, MemberCapacity],
) -> FrameDesignWorkflowResult:
    if not loads_by_combination:
        raise ValueError("at least one load combination is required")
    element_ids = {element.id for element in elements}
    if set(capacities_by_member) != element_ids:
        raise ValueError("capacities must be supplied for every frame element")
    analyses: dict[str, LinearFrameResult] = {}
    demands: dict[int, dict[str, MemberDemand]] = {element.id: {} for element in elements}
    for combination, loads in loads_by_combination.items():
        if not combination.strip():
            raise ValueError("combination names cannot be blank")
        if combination in analyses:
            raise ValueError(f"duplicate combination: {combination}")
        result = solve_linear_frame(nodes, elements, loads)
        analyses[combination] = result
        for element in elements:
            forces = result.member_end_forces_local[element.id]
            demands[element.id][combination] = MemberDemand(
                axial=max(abs(forces[0]), abs(forces[3])),
                moment=max(abs(forces[2]), abs(forces[5])),
            )
    checks = {member_id: check_governing_axial_flexure(member_demands, capacities_by_member[member_id]) for member_id, member_demands in demands.items()}
    return FrameDesignWorkflowResult(analyses_by_combination=analyses, demands_by_member=demands, checks_by_member=checks)