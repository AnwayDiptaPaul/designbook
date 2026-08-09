"""Deterministic analysis execution state and provenance contracts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Mapping


class AnalysisState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


_ALLOWED: dict[AnalysisState, frozenset[AnalysisState]] = {
    AnalysisState.PENDING: frozenset({AnalysisState.RUNNING, AnalysisState.CANCELLED}),
    AnalysisState.RUNNING: frozenset({AnalysisState.COMPLETED, AnalysisState.FAILED, AnalysisState.CANCELLED}),
    AnalysisState.COMPLETED: frozenset(),
    AnalysisState.FAILED: frozenset(),
    AnalysisState.CANCELLED: frozenset(),
}


def can_transition(current: AnalysisState, target: AnalysisState) -> bool:
    return target in _ALLOWED[current]


def require_transition(current: AnalysisState, target: AnalysisState) -> AnalysisState:
    if not can_transition(current, target):
        raise ValueError(f"invalid analysis status transition: {current.value} -> {target.value}")
    return target


@dataclass(frozen=True, slots=True)
class ExecutionProvenance:
    revision_id: str
    snapshot_hash: str
    code_standard: str
    code_edition: str
    engine: str
    engine_version: str
    created_at: str

    @classmethod
    def create(cls, *, revision_id: str, snapshot_hash: str, code_standard: str, code_edition: str, engine: str, engine_version: str) -> "ExecutionProvenance":
        values = (revision_id, snapshot_hash, code_standard, code_edition, engine, engine_version)
        if any(not value.strip() for value in values):
            raise ValueError("execution provenance fields cannot be blank")
        return cls(revision_id, snapshot_hash, code_standard, code_edition, engine, engine_version, datetime.now(timezone.utc).isoformat())

    def as_dict(self) -> Mapping[str, str]:
        return {
            "revision_id": self.revision_id,
            "snapshot_hash": self.snapshot_hash,
            "code_standard": self.code_standard,
            "code_edition": self.code_edition,
            "engine": self.engine,
            "engine_version": self.engine_version,
            "created_at": self.created_at,
        }