"""Immutable project-revision records used as calculation inputs."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RevisionStatus(str, enum.Enum):
    DRAFT = "draft"
    FROZEN = "frozen"
    SUPERSEDED = "superseded"


class ProjectRevision(Base):
    """A versioned, hash-addressed snapshot of project engineering inputs."""

    __tablename__ = "project_revisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    parent_revision_id = Column(UUID(as_uuid=True), ForeignKey("project_revisions.id"), nullable=True)
    revision_number = Column(Integer, nullable=False)
    status = Column(SAEnum(RevisionStatus), nullable=False, default=RevisionStatus.DRAFT)
    snapshot_hash = Column(String(64), nullable=False, index=True)
    snapshot = Column(JSON, nullable=False, default=dict)
    note = Column(Text, nullable=True)
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    frozen_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="revisions")
    parent = relationship("ProjectRevision", remote_side=[id], uselist=False)
    analysis_runs = relationship("AnalysisRun", back_populates="revision")
