# pyre-ignore-all-errors
"""SQLAlchemy ORM models — AnalysisRun, AnalysisResult."""

import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Integer, Float, Enum as SAEnum,
    ForeignKey, JSON, DateTime, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class AnalysisType(str, enum.Enum):
    LINEAR_ELASTIC = "linear_elastic"
    PDELTA = "pdelta"
    MODAL = "modal"
    RESPONSE_SPECTRUM = "response_spectrum"
    TIME_HISTORY = "time_history"
    PUSHOVER = "pushover"


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    revision_id = Column(UUID(as_uuid=True), ForeignKey("project_revisions.id", ondelete="SET NULL"), nullable=True)

    analysis_type = Column(SAEnum(AnalysisType), nullable=False)
    status = Column(SAEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    progress_pct = Column(Integer, default=0)
    celery_task_id = Column(String(255))

    # Config for this run (load combos, options, etc.)
    config = Column(JSON, default=dict)

    # Summary results (base shear, periods, etc.)
    summary = Column(JSON, default=dict)

    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=_utcnow)

    project = relationship("Project", back_populates="analysis_runs")
    revision = relationship("ProjectRevision", back_populates="analysis_runs")
    results = relationship("AnalysisResult", back_populates="analysis_run", cascade="all, delete-orphan")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_run_id = Column(UUID(as_uuid=True), ForeignKey("analysis_runs.id", ondelete="CASCADE"))
    member_id = Column(UUID(as_uuid=True), ForeignKey("structural_members.id", ondelete="CASCADE"), nullable=True)

    result_type = Column(String(50))  # "member_forces", "nodal_displacements", "story_drift", "mode_shape"

    # Flexible result data
    data = Column(JSON, default=dict)

    analysis_run = relationship("AnalysisRun", back_populates="results")
