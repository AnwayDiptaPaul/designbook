# pyre-ignore-all-errors
"""API routes — Project CRUD."""


from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database import get_db
from backend.models.project import Project, BuildingInfo, SiteData
from backend.api.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectRead, ProjectList,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=list[ProjectList])
async def list_projects(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List all projects with pagination."""
    result = await db.execute(
        select(Project).order_by(Project.updated_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new project with optional building info and site data."""
    project = Project(
        name=payload.name,
        location=payload.location,
        client_name=payload.client_name,
        engineer_name=payload.engineer_name,
        design_code=payload.design_code,
        occupancy=payload.occupancy,
        description=payload.description,
    )
    if payload.building:
        project.building = BuildingInfo(**payload.building.model_dump())
    if payload.site:
        project.site = SiteData(**payload.site.model_dump())

    db.add(project)
    await db.flush()
    await db.refresh(project, attribute_names=["building", "site"])
    return project


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a project by ID with building info and site data."""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.building), selectinload(Project.site))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Partially update a project."""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.building), selectinload(Project.site))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    project.revision += 1
    await db.flush()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a project and all related data."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
