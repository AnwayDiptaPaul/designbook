# pyre-ignore-all-errors
"""Pydantic v2 schemas — Project, BuildingInfo, SiteData, Grid, Floor."""

from __future__ import annotations
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field, model_validator


# ── Enums (re-export from models for schema use) ─────────

from backend.models.project import (
    BuildingOccupancy, SeismicZone, SoilClass,
    WindExposure, FrameType, DesignCode,
)


# ── Building Info ────────────────────────────────────────

class BuildingInfoBase(BaseModel):
    num_basements: int = Field(default=0, ge=0, le=20)
    num_ground_floors: int = Field(default=1, ge=1, le=10)
    num_typical_floors: int = Field(default=5, ge=0, le=200)
    num_penthouse_floors: int = Field(default=0, ge=0, le=20)
    total_height_m: Optional[float] = Field(default=None, gt=0, le=1000)
    frame_type: FrameType = FrameType.OMRF


class BuildingInfoCreate(BuildingInfoBase):
    pass


class BuildingInfoRead(BuildingInfoBase):
    id: UUID
    project_id: UUID
    model_config = {"from_attributes": True}


# ── Site Data ────────────────────────────────────────────

class SiteDataBase(BaseModel):
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    seismic_zone: SeismicZone = SeismicZone.II
    soil_class: SoilClass = SoilClass.SD
    wind_exposure: WindExposure = WindExposure.B
    basic_wind_speed_mps: float = Field(default=47.0, gt=0, le=150)
    terrain_category: int = Field(default=2, ge=1, le=4)
    topographic_factor: float = Field(default=1.0, gt=0, le=5)
    site_elevation_m: float = Field(default=0.0, ge=-500, le=10000)

    @model_validator(mode="after")
    def validate_coordinates(self) -> "SiteDataBase":
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be supplied together")
        return self


class SiteDataCreate(SiteDataBase):
    pass


class SiteDataRead(SiteDataBase):
    id: UUID
    project_id: UUID
    model_config = {"from_attributes": True}


# ── Grid Definition ──────────────────────────────────────

class GridDefinitionBase(BaseModel):
    axis: str = Field(..., pattern=r"^[XY]$")
    label: str = Field(..., min_length=1, max_length=10)
    position_m: float = Field(..., ge=0, le=10000)


class GridDefinitionCreate(GridDefinitionBase):
    pass


class GridDefinitionRead(GridDefinitionBase):
    id: UUID
    project_id: UUID
    model_config = {"from_attributes": True}


# ── Floor Definition ─────────────────────────────────────

class FloorDefinitionBase(BaseModel):
    floor_number: int = Field(..., ge=-20, le=300)
    label: Optional[str] = Field(default=None, max_length=50)
    height_m: float = Field(..., gt=0, le=100)
    elevation_m: Optional[float] = Field(default=None, ge=-500, le=10000)


class FloorDefinitionCreate(FloorDefinitionBase):
    pass


class FloorDefinitionRead(FloorDefinitionBase):
    id: UUID
    project_id: UUID
    model_config = {"from_attributes": True}


# ── Project ──────────────────────────────────────────────

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    location: Optional[str] = Field(default=None, max_length=500)
    client_name: Optional[str] = Field(default=None, max_length=255)
    engineer_name: Optional[str] = Field(default=None, max_length=255)
    design_code: DesignCode = DesignCode.BNBC_2020
    occupancy: BuildingOccupancy = BuildingOccupancy.RESIDENTIAL
    description: Optional[str] = Field(default=None, max_length=5000)


class ProjectCreate(ProjectBase):
    building: Optional[BuildingInfoCreate] = None
    site: Optional[SiteDataCreate] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=255)
    location: Optional[str] = Field(default=None, max_length=500)
    client_name: Optional[str] = Field(default=None, max_length=255)
    engineer_name: Optional[str] = Field(default=None, max_length=255)
    design_code: Optional[DesignCode] = None
    occupancy: Optional[BuildingOccupancy] = None
    description: Optional[str] = Field(default=None, max_length=5000)


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
