"""Deterministic review-oriented projections of design workflow results."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping

from .audit import AnalysisAuditRecord
from .workflow import FrameDesignWorkflowResult

EQUILIBRIUM_TOLERANCE = 1e-8

@dataclass(frozen=True, slots=True)
class MemberDesignSummary:
    member_id: int
    governing_combination: str
    utilization: float
    status: str

@dataclass(frozen=True, slots=True)
class FrameDesignReport:
    overall_status: str
    members: tuple[MemberDesignSummary, ...]
    audit: Mapping[str, Any]
    warnings: tuple[str, ...]
    max_free_dof_residual: float

    def as_dict(self) -> Mapping[str, Any]:
        return {
            "overall_status": self.overall_status,
            "members": [{"member_id": item.member_id, "governing_combination": item.governing_combination, "utilization": item.utilization, "status": item.status} for item in self.members],
            "audit": dict(self.audit),
            "warnings": list(self.warnings),
            "max_free_dof_residual": self.max_free_dof_residual,
        }


def build_frame_design_report(workflow: FrameDesignWorkflowResult, audit: AnalysisAuditRecord) -> FrameDesignReport:
    members = tuple(
        MemberDesignSummary(member_id=member_id, governing_combination=result.combination, utilization=result.check.utilization, status=result.check.status)
        for member_id, result in sorted(workflow.checks_by_member.items())
    )
    warnings = list(audit.warnings)
    if any(result.check.capacity.review_status == "prototype" for result in workflow.checks_by_member.values()):
        warnings.append("one or more capacity providers are prototype-level")
    max_residual = max((analysis.free_dof_residual_max for analysis in workflow.analyses_by_combination.values()), default=0.0)
    if max_residual > EQUILIBRIUM_TOLERANCE:
        warnings.append(f"free-DOF equilibrium residual exceeds tolerance ({max_residual:.3e} > {EQUILIBRIUM_TOLERANCE:.1e})")
    unique_warnings = tuple(dict.fromkeys(warnings))
    return FrameDesignReport(
        overall_status="pass" if all(item.status == "pass" for item in members) and max_residual <= EQUILIBRIUM_TOLERANCE else "fail",
        members=members,
        audit=audit.as_dict(),
        warnings=unique_warnings,
        max_free_dof_residual=max_residual,
    )