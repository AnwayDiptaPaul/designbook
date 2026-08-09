"""Canonical, dependency-light domain primitives for DesignBook.

The domain package deliberately avoids FastAPI, SQLAlchemy, OpenSeesPy, and
frontend concerns.  It is the stable seam used by API contracts, persistence,
workers, and verification fixtures.
"""

from .snapshots import canonical_json, snapshot_hash
from .units import Quantity, UnitSystem, convert, ensure_positive

__all__ = [
    "Quantity",
    "UnitSystem",
    "canonical_json",
    "convert",
    "ensure_positive",
    "snapshot_hash",
]
