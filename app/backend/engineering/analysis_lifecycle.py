"""Explicit state-transition rules for persisted analysis runs."""

from __future__ import annotations

from enum import Enum
from typing import Any


_ALLOWED: dict[str, frozenset[str]] = {
    "pending": frozenset({"running", "cancelled"}),
    "running": frozenset({"completed", "failed", "cancelled"}),
    "completed": frozenset(),
    "failed": frozenset(),
    "cancelled": frozenset(),
}


def _state_value(state: Any) -> str:
    value = state.value if isinstance(state, Enum) else state
    return str(value)


def can_transition(current: Any, target: Any) -> bool:
    """Return whether a persisted run may move between two states."""

    return _state_value(target) in _ALLOWED.get(_state_value(current), frozenset())


def require_transition(current: Any, target: Any) -> None:
    """Raise a clear error when a state transition would violate the lifecycle."""

    if not can_transition(current, target):
        raise ValueError(f"invalid analysis state transition: {_state_value(current)} -> {_state_value(target)}")