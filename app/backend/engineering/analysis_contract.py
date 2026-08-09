"""Validation and canonicalization for persisted analysis requests."""

from __future__ import annotations

from typing import Any

from backend.domain.snapshots import canonical_json, snapshot_hash


class AnalysisContractError(ValueError):
    """Raised when an analysis request cannot be safely persisted."""


def prepare_run_config(config: Any) -> dict[str, Any]:
    """Return a validated, hash-addressed copy of a run configuration.

    Persisted runs must carry their complete immutable input snapshot. The
    hash is stored alongside it so workers and reviewers can verify that the
    snapshot was not changed after queueing.
    """

    if not isinstance(config, dict):
        raise AnalysisContractError("analysis config must be an object")
    snapshot = config.get("snapshot")
    if not isinstance(snapshot, dict) or not snapshot:
        raise AnalysisContractError("config.snapshot is required for persisted analysis")
    try:
        canonical_json(snapshot)
    except (TypeError, ValueError) as exc:
        raise AnalysisContractError("config.snapshot must contain JSON-safe finite values") from exc
    expected_hash = snapshot_hash(snapshot)
    supplied_hash = config.get("snapshot_hash")
    if supplied_hash is not None and supplied_hash != expected_hash:
        raise AnalysisContractError("config.snapshot_hash does not match config.snapshot")
    prepared = dict(config)
    prepared["snapshot"] = snapshot
    prepared["snapshot_hash"] = expected_hash
    return prepared


def verify_run_config(config: Any) -> dict[str, Any]:
    """Validate an immutable persisted config and return its normalized copy."""

    prepared = prepare_run_config(config)
    if config.get("snapshot_hash") != prepared["snapshot_hash"]:
        raise AnalysisContractError("persisted config is missing its snapshot_hash")
    return prepared