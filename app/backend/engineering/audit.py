"""Reproducible calculation audit records."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from backend.domain.snapshots import snapshot_hash

@dataclass(frozen=True, slots=True)
class AnalysisAuditRecord:
    input_hash: str
    output_hash: str
    solver: str
    solver_version: str
    standard: str
    edition: str
    created_at: str
    warnings: tuple[str, ...] = ()

    @classmethod
    def create(cls, *, model: Any, configuration: Any, output: Any, solver: str, solver_version: str, standard: str, edition: str, warnings: tuple[str, ...] = ()) -> "AnalysisAuditRecord":
        values = (solver, solver_version, standard, edition)
        if any(not value.strip() for value in values):
            raise ValueError("audit metadata fields cannot be blank")
        if any(not isinstance(warning, str) or not warning.strip() for warning in warnings):
            raise ValueError("audit warnings must be non-blank strings")
        return cls(
            input_hash=snapshot_hash({"model": model, "configuration": configuration}),
            output_hash=snapshot_hash(output),
            solver=solver,
            solver_version=solver_version,
            standard=standard,
            edition=edition,
            created_at=datetime.now(timezone.utc).isoformat(),
            warnings=tuple(warnings),
        )

    def as_dict(self) -> Mapping[str, Any]:
        return {
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "solver": self.solver,
            "solver_version": self.solver_version,
            "standard": self.standard,
            "edition": self.edition,
            "created_at": self.created_at,
            "warnings": list(self.warnings),
        }