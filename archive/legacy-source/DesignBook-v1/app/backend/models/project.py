"""SQLAlchemy ORM models — Project, Building, Site, Grid."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean, DateTime, Enum as SAEnum,
    ForeignKey, JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


# ── Enums ────────────────────────────────────────────────


import enum


class BuildingOccupancy(str, enum.Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED = "mixed"


class SeismicZone(str, enum.Enum):
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"


class SoilClass(str, enum.Enum):
    SA = "SA"
    SB = "SB"
    SC = "SC"
    SD = "SD"
    SE = "SE"


class WindExposure(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class FrameType(str, enum.Enum):
    OMRF = "OMRF"
    IMRF = "IMRF"
    SMRF = "SMRF"


class DesignCode(str, enum.Enum):
    BNBC_2020 = "BNBC_2020"
    ACI_318_19 = "ACI_318_19"


# ── Project ──────────────────────────────────────────────


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    location = Column(String(500))
    client_name = Column(String(255))
    engineer_name = Column(String(255))
    date = Column(DateTime, default=_utcnow)
    revision = Column(Integer, default=1)
    design_code = Column(SAEnum(DesignCode), default=DesignCode.BNBC_2020)
    occupancy = Column(SAEnum(BuildingOccupancy), default=BuildingOccupancy.RESIDENTIAL)
    description = Column(Text)

    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    building = relationship("BuildingInfo", back_populates="project", uselist=False, cascade="all, delete-orphan")
    site = relationship("SiteData", back_populates="project", uselist=False, cascade="all, delete-orphan")
    grids = relationship("GridDefinition", back_populates="project", cascade="all, delete-orphan")
    floors = relationship("FloorDefinition", back_populates="project", cascade="all, delete-orphan")
    members = relationship("StructuralMember", back_populates="project", cascade="all, delete-orphan")
    load_cases = relationship("LoadCase", back_populates="project", cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRun", back_populates="project", cascade="all, delete-orphan")


# ── Building Info ────────────────────────────────────────


class BuildingInfo(Base):
    __tablename__ = "building_info"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), unique=True)

    num_basements = Column(Integer, default=0)
    num_ground_floors = Column(Integer, default=1)
    num_typical_floors = Column(Integer, default=5)
    num_penthouse_floors = Column(Integer, default=0)
    total_height_m = Column(Float)
    frame_type = Column(SAEnum(FrameType), default=FrameType.OMRF)

    project = relationship("Project", back_populates="building")


# ── Site Data ────────────────────────────────────────────


class SiteData(Base):
    __tablename__ = "site_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), unique=True)

    latitude = Column(Float)
    longitude = Column(Float)
    seismic_zone = Column(SAEnum(SeismicZone), default=SeismicZone.II)
    soil_class = Column(SAEnum(SoilClass), default=SoilClass.SD)
    wind_exposure = Column(SAEnum(WindExposure), default=WindExposure.B)
    basic_wind_speed_mps = Column(Float, default=47.0)  # m/s
    terrain_category = Column(Integer, default=2)
    topographic_factor = Column(Float, default=1.0)
    site_elevation_m = Column(Float, default=0.0)

    project = relationship("Project", back_populates="site")


# ── Grid & Floor ─────────────────────────────────────────


class GridDefinition(Base):
    __tablename__ = "grid_definitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))

    axis = Column(String(1))  # 'X' or 'Y'
    label = Column(String(10))  # 'A', 'B', '1', '2' etc.
    position_m = Column(Float, nullable=False)  # distance from origin in metres

    project = relationship("Project", back_populates="grids")


class FloorDefinition(Base):
    __tablename__ = "floor_definitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))

    floor_number = Column(Integer, nullable=False)  # -1 = B1, 0 = Ground, 1+
    label = Column(String(50))  # "Basement-1", "Ground", "1st", "Roof"
    height_m = Column(Float, nullable=False)  # floor-to-floor height
    elevation_m = Column(Float)  # cumulative elevation from datum

    project = relationship("Project", back_populates="floors")
