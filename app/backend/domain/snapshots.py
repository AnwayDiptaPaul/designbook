"""Canonical serialization and immutable input snapshot identifiers."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    """Serialize JSON-compatible data deterministically for hashing/storage."""

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def snapshot_hash(value: Any) -> str:
    """Return a SHA-256 identifier for a calculation input snapshot."""

    payload = canonical_json(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
