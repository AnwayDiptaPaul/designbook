"""Pydantic v2 schemas — StructuralMember."""

from __future__ import annotations
from uuid import UUID
from typing import Optional, Any

from pydantic import BaseModel, Field

from backend.models.member import MemberType, MemberStatus, ConcreteGrade, SteelGrade


class MemberBase(BaseModel):
    label: Optional[str] = None
    member_type: MemberType
    floor_number: Optional[int] = None
    width_mm: Optional[float] = None
    depth_mm: Optional[float] = None
    length_mm: Optional[float] = None
    clear_cover_mm: float = 40.0
    concrete_grade_mpa: ConcreteGrade = ConcreteGrade.C25
    steel_grade_mpa: SteelGrade = SteelGrade.FY500
    grid_start: Optional[str] = None
    grid_end: Optional[str] = None
    orientation: Optional[str] = None
    local_axes_rotation_deg: float = 0.0
    properties: dict[str, Any] = {}


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    label: Optional[str] = None
    width_mm: Optional[float] = None
    depth_mm: Optional[float] = None
    length_mm: Optional[float] = None
    clear_cover_mm: Optional[float] = None
    concrete_grade_mpa: Optional[ConcreteGrade] = None
    steel_grade_mpa: Optional[SteelGrade] = None
    grid_start: Optional[str] = None
    grid_end: Optional[str] = None
    orientation: Optional[str] = None
    properties: Optional[dict[str, Any]] = None


class MemberRead(MemberBase):
    id: UUID
    project_id: UUID
    status: MemberStatus
    design_results: dict[str, Any] = {}
    model_config = {"from_attributes": True}
