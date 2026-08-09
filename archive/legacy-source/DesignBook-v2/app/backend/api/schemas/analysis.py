"""Pydantic v2 schemas — AnalysisRun, AnalysisResult."""

from __future__ import annotations
from datetime import datetime
from uuid import UUID
from typing import Optional, Any

from pydantic import BaseModel

from backend.models.analysis import AnalysisType, AnalysisStatus


class AnalysisRunCreate(BaseModel):
    analysis_type: AnalysisType
    config: dict[str, Any] = {}


class AnalysisRunRead(BaseModel):
    id: UUID
    project_id: UUID
    analysis_type: AnalysisType
    status: AnalysisStatus
    progress_pct: int
    celery_task_id: Optional[str] = None
    config: dict[str, Any] = {}
    summary: dict[str, Any] = {}
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class AnalysisResultRead(BaseModel):
    id: UUID
    analysis_run_id: UUID
    member_id: Optional[UUID] = None
    result_type: Optional[str] = None
    data: dict[str, Any] = {}
    model_config = {"from_attributes": True}
