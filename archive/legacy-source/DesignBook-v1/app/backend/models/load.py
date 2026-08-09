"""SQLAlchemy ORM models — LoadCase, LoadCombination."""

import uuid
import enum

from sqlalchemy import (
    Column, String, Integer, Float, Enum as SAEnum,
    ForeignKey, JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database import Base


class LoadType(str, enum.Enum):
    DEAD = "dead"
    LIVE = "live"
    SUPERIMPOSED_DEAD = "superimposed_dead"
    WIND_X_POS = "wind_x_pos"
    WIND_X_NEG = "wind_x_neg"
    WIND_Y_POS = "wind_y_pos"
    WIND_Y_NEG = "wind_y_neg"
    SEISMIC_X = "seismic_x"
    SEISMIC_Y = "seismic_y"
    TEMPERATURE = "temperature"
    HYDROSTATIC = "hydrostatic"
    SOIL_LATERAL = "soil_lateral"


class LoadCase(Base):
    __tablename__ = "load_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))

    name = Column(String(100), nullable=False)
    load_type = Column(SAEnum(LoadType), nullable=False)
    description = Column(String(500))

    # Load values stored as JSON for flexibility:
    # For DL/LL: {"area_load_kpa": 3.0, "line_load_knm": 10.0, "point_load_kn": 50.0}
    # For Wind:  {"story_forces": [{"floor": 1, "force_kn": 23.5}, ...]}
    # For Seismic: {"base_shear_kn": 450.0, "story_forces": [...]}
    values = Column(JSON, default=dict)

    project = relationship("Project", back_populates="load_cases")


class LoadCombination(Base):
    __tablename__ = "load_combinations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))

    name = Column(String(50), nullable=False)       # "U1", "U2", ..., "S1", ...
    combo_type = Column(String(20), default="strength")  # "strength" or "serviceability"

    # Factor mapping: {"dead": 1.2, "live": 1.6, "wind_x_pos": 0.5, ...}
    factors = Column(JSON, nullable=False)
