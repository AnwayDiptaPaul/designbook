"""Pydantic v2 schemas — Project, BuildingInfo, SiteData, Grid, Floor."""

from __future__ import annotations
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums (re-export from models for schema use) ─────────

from backend.models.project import (
    BuildingOccupancy, SeismicZone, SoilClass,
    WindExposure, FrameType, DesignCode,
)


# ── Building Info ────────────────────────────────────────

class BuildingInfoBase(BaseModel):
    num_basements: int = 0
    num_ground_floors: int = 1
    num_typical_floors: int = 5
    num_penthouse_floors: int = 0
    total_height_m: Optional[float] = None
    frame_type: FrameType = FrameType.OMRF


class BuildingInfoCreate(BuildingInfoBase):
    pass


class BuildingInfoRead(BuildingInfoBase):
    id: UUID
    project_id: UUID
    model_config = {"from_attributes": True}


# ── Site Data ────────────────────────────────────────────

class SiteDataBase(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    seismic_zone: SeismicZone = SeismicZone.II
    soil_class: SoilClass = SoilClass.SD
    wind_exposure: WindExposure = WindExposure.B
    basic_wind_speed_mps: float = 47.0
    terrain_category: int = 2
    topographic_factor: float = 1.0
    site_elevation_m: float = 0.0


class SiteDataCreate(SiteDataBase):
    pass


class SiteDataRead(SiteDataBase):
    id: UUID
    project_id: UUID
    model_config = {"from_attributes": True}


# ── Grid Definition ──────────────────────────────────────

class GridDefinitionBase(BaseModel):
    axis: str = Field(..., pattern=r"^[XY]$")
    label: str = Field(..., max_length=10)
    position_m: float


class GridDefinitionCreate(GridDefinitionBase):
    pass


class GridDefinitionRead(GridDefinitionBase):
    id: UUID
    project_id: UUID
    model_config = {"from_attributes": True}


# ── Floor Definition ─────────────────────────────────────

class FloorDefinitionBase(BaseModel):
    floor_number: int
    label: Optional[str] = None
    height_m: float
    elevation_m: Optional[float] = None


class FloorDefinitionCreate(FloorDefinitionBase):
    pass


class FloorDefinitionRead(FloorDefinitionBase):
    id: UUID
    project_id: UUID
    model_config = {"from_attributes": True}


# ── Project ──────────────────────────────────────────────

class ProjectBase(BaseModel):
    name: str = Field(..., max_length=255)
    location: Optional[str] = None
    client_name: Optional[str] = None
    engineer_name: Optional[str] = None
    design_code: DesignCode = DesignCode.BNBC_2020
    occupancy: BuildingOccupancy = BuildingOccupancy.RESIDENTIAL
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    building: Optional[BuildingInfoCreate] = None
    site: Optional[SiteDataCreate] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    engineer_name: Optional[str] = None
    design_code: Optional[DesignCode] = None
    occupancy: Optional[BuildingOccupancy] = None
    description: Optional[str] = None


class ProjectRead(ProjectBase):
    id: UUID
    revision: int
    created_at: datetime
    updated_at: datetime
    building: Optional[BuildingInfoRead] = None
    site: Optional[SiteDataRead] = None
    model_config = {"from_attributes": True}


class ProjectList(BaseModel):
    id: UUID
    name: str
    location: Optional[str] = None
    occupancy: BuildingOccupancy
    design_code: DesignCode
    revision: int
    updated_at: datetime
    model_config = {"from_attributes": True}
