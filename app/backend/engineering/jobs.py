"""Dependency-light analysis job command and idempotency contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Mapping
import json

from .execution import AnalysisState, ExecutionProvenance, require_transition


def request_fingerprint(*, project_id: str, revision_id: str, analysis_type: str, config: Mapping[str, Any]) -> str:
    payload = {"project_id": project_id, "revision_id": revision_id, "analysis_type": analysis_type, "config": config}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class AnalysisJobCommand:
    project_id: str
    revision_id: str
    analysis_type: str
    config: Mapping[str, Any]
    idempotency_key: str

    @classmethod
    def create(cls, *, project_id: str, revision_id: str, analysis_type: str, config: Mapping[str, Any], idempotency_key: str) -> "AnalysisJobCommand":
        values = (project_id, revision_id, analysis_type, idempotency_key)
        if any(not value.strip() for value in values):
            raise ValueError("job command identifiers cannot be blank")
        return cls(project_id, revision_id, analysis_type, dict(config), idempotency_key)

    def fingerprint(self) -> str:
        return request_fingerprint(project_id=self.project_id, revision_id=self.revision_id, analysis_type=self.analysis_type, config=self.config)


@dataclass(slots=True)
class AnalysisJobRecord:
    command: AnalysisJobCommand
    status: AnalysisState = AnalysisState.PENDING
    provenance: ExecutionProvenance | None = None
    error: str | None = None
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def transition(self, target: AnalysisState, *, error: str | None = None) -> None:
        require_transition(self.status, target)
        if target is AnalysisState.FAILED and not error:
            raise ValueError("failed jobs require an error")
        self.status = target
        self.error = error
        self.updated_at = datetime.now(timezone.utc).isoformat()


class InMemoryJobIndex:
    """Small deterministic reference implementation for API/service tests."""

    def __init__(self) -> None:
        self._records: dict[str, AnalysisJobRecord] = {}

    def submit(self, command: AnalysisJobCommand) -> tuple[AnalysisJobRecord, bool]:
        key = command.idempotency_key
        existing = self._records.get(key)
        if existing is not None:
            if existing.command.fingerprint() != command.fingerprint():
                raise ValueError("idempotency key was reused for a different analysis command")
            return existing, False
        record = AnalysisJobRecord(command=command)
        self._records[key] = record
        return record, True