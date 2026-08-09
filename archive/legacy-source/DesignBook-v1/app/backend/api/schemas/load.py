"""Pydantic v2 schemas — LoadCase, LoadCombination."""

from __future__ import annotations
from uuid import UUID
from typing import Optional, Any

from pydantic import BaseModel

from backend.models.load import LoadType


class LoadCaseBase(BaseModel):
    name: str
    load_type: LoadType
    description: Optional[str] = None
    values: dict[str, Any] = {}


class LoadCaseCreate(LoadCaseBase):
    pass


class LoadCaseRead(LoadCaseBase):
    id: UUID
    project_id: UUID
    model_config = {"from_attributes": True}


class LoadCombinationBase(BaseModel):
    name: str
    combo_type: str = "strength"
    factors: dict[str, float]


class LoadCombinationCreate(LoadCombinationBase):
    pass


class LoadCombinationRead(LoadCombinationBase):
    id: UUID
    project_id: UUID
    model_config = {"from_attributes": True}
