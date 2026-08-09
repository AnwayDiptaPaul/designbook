"""API contracts for immutable project input revisions."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class RevisionStatus(str, Enum):
    DRAFT = "draft"
    FROZEN = "frozen"
    SUPERSEDED = "superseded"


class ProjectRevisionCreate(BaseModel):
    snapshot: dict[str, Any] = Field(default_factory=dict)
    note: str | None = Field(default=None, max_length=2000)
    created_by: str | None = Field(default=None, max_length=255)


class ProjectRevisionRead(BaseModel):
    id: UUID
    project_id: UUID
    parent_revision_id: UUID | None
    revision_number: int
    status: RevisionStatus
    snapshot_hash: str
    snapshot: dict[str, Any]
    note: str | None
    created_by: str | None
    created_at: datetime
    frozen_at: datetime | None

    model_config = {"from_attributes": True}
