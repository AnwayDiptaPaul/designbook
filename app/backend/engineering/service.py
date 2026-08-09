"""Revision-snapshot analysis service boundary."""
from __future__ import annotations
from typing import Any, Mapping

from .audit import AnalysisAuditRecord
from .design.checks import MemberCapacity
from .frame_solver import FrameElement2D, FrameNode2D
from .reporting import FrameDesignReport, build_frame_design_report
from .workflow import run_frame_design_workflow


def run_snapshot_analysis(snapshot: Mapping[str, Any], configuration: Mapping[str, Any]) -> FrameDesignReport:
    if not isinstance(snapshot, Mapping) or not isinstance(configuration, Mapping):
        raise ValueError("snapshot and configuration must be mappings")
    nodes = _nodes(snapshot.get("nodes"))
    elements = _elements(snapshot.get("elements"))
    loads = _loads(snapshot.get("loads_by_combination"))
    capacities = _capacities(snapshot.get("capacities"), {element.id for element in elements})
    workflow = run_frame_design_workflow(nodes, elements, loads, capacities)
    output = {"members": {str(member_id): {"combination": result.combination, "utilization": result.check.utilization, "status": result.check.status} for member_id, result in workflow.checks_by_member.items()}}
    audit = AnalysisAuditRecord.create(model=snapshot, configuration=configuration, output=output, solver="designbook-linear-frame", solver_version="0.1", standard=str(configuration.get("standard", "prototype")), edition=str(configuration.get("edition", "0.1")), warnings=("capacity providers must be independently reviewed",))
    return build_frame_design_report(workflow, audit)


def _nodes(raw: Any) -> tuple[FrameNode2D, ...]:
    if not isinstance(raw, list) or not raw:
        raise ValueError("snapshot.nodes must be a non-empty list")
    try:
        return tuple(FrameNode2D(int(item["id"]), float(item["x"]), float(item["y"]), bool(item.get("fix_x", False)), bool(item.get("fix_y", False)), bool(item.get("fix_rotation", False))) for item in raw)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("invalid snapshot node") from exc


def _elements(raw: Any) -> tuple[FrameElement2D, ...]:
    if not isinstance(raw, list) or not raw:
        raise ValueError("snapshot.elements must be a non-empty list")
    try:
        return tuple(FrameElement2D(int(item["id"]), int(item["start"]), int(item["end"]), float(item["area"]), float(item["elastic_modulus"]), float(item["moment_of_inertia"])) for item in raw)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("invalid snapshot element") from exc


def _loads(raw: Any) -> Mapping[str, Mapping[int, tuple[float, float, float]]]:
    if not isinstance(raw, Mapping) or not raw:
        raise ValueError("snapshot.loads_by_combination must be a non-empty mapping")
    try:
        return {str(combination): {int(node_id): (float(values[0]), float(values[1]), float(values[2])) for node_id, values in cases.items()} for combination, cases in raw.items()}
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        raise ValueError("invalid snapshot load combination") from exc


def _capacities(raw: Any, element_ids: set[int]) -> Mapping[int, MemberCapacity]:
    if not isinstance(raw, Mapping) or set(int(key) for key in raw) != element_ids:
        raise ValueError("snapshot.capacities must define every element")
    result: dict[int, MemberCapacity] = {}
    try:
        for key, value in raw.items():
            result[int(key)] = MemberCapacity(float(value["axial"]), float(value["moment"]), str(value["standard"]), str(value["edition"]), str(value["reference"]), str(value.get("review_status", "prototype")))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("invalid snapshot capacity") from exc
    return result