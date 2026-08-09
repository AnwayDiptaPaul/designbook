# pyre-ignore-all-errors
"""SQLAlchemy ORM models — Structural Members (polymorphic)."""

import uuid
import enum

from sqlalchemy import (
    Column, String, Integer, Float, Enum as SAEnum,
    ForeignKey, JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database import Base


class MemberType(str, enum.Enum):
    BEAM = "beam"
    COLUMN = "column"
    SLAB_ONEWAY = "slab_oneway"
    SLAB_TWOWAY = "slab_twoway"
    SLAB_BEAMLESS = "slab_beamless"
    SHEAR_WALL = "shear_wall"
    RETAINING_WALL = "retaining_wall"
    FOOTING_ISOLATED = "footing_isolated"
    FOOTING_COMBINED = "footing_combined"
    FOOTING_RAFT = "footing_raft"
    STAIRCASE = "staircase"
    DOME = "dome"


class MemberStatus(str, enum.Enum):
    NOT_DESIGNED = "not_designed"
    DESIGNING = "designing"
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


class ConcreteGrade(str, enum.Enum):
    C20 = "20"
    C25 = "25"
    C28 = "28"
    C30 = "30"
    C35 = "35"


class SteelGrade(str, enum.Enum):
    FY250 = "250"
    FY415 = "415"
    FY500 = "500"


class StructuralMember(Base):
    __tablename__ = "structural_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))

    label = Column(String(50))             # e.g. "B-01", "C-A1-1"
    member_type = Column(SAEnum(MemberType), nullable=False)
    floor_number = Column(Integer)         # which floor level
    status = Column(SAEnum(MemberStatus), default=MemberStatus.NOT_DESIGNED)

    # ── Geometry (common) ─────────────────────────────────
    width_mm = Column(Float)               # b
    depth_mm = Column(Float)               # h (or d for slab thickness)
    length_mm = Column(Float)              # span or height
    clear_cover_mm = Column(Float, default=40.0)

    # ── Material ──────────────────────────────────────────
    concrete_grade_mpa = Column(SAEnum(ConcreteGrade), default=ConcreteGrade.C25)
    steel_grade_mpa = Column(SAEnum(SteelGrade), default=SteelGrade.FY500)

    # ── Placement ─────────────────────────────────────────
    grid_start = Column(String(20))       # e.g. "A-1"
    grid_end = Column(String(20))         # e.g. "A-2"
    orientation = Column(String(5))       # "X", "Y", "Z"
    local_axes_rotation_deg = Column(Float, default=0.0)

    # ── Type-specific data (flexible JSON) ────────────────
    properties = Column(JSON, default=dict)

    # ── Design results (populated after design) ───────────
    design_results = Column(JSON, default=dict)

    # ── Relationships ─────────────────────────────────────
    project = relationship("Project", back_populates="members")
