"""Project revision endpoints.

Revision records are append-only. Updating an engineering input must create a
new revision rather than mutating a snapshot used by an analysis run.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.revision import ProjectRevisionCreate, ProjectRevisionRead
from backend.database import get_db
from backend.domain.snapshots import snapshot_hash
from backend.models.project import Project
from backend.models.revision import ProjectRevision, RevisionStatus

router = APIRouter(prefix="/projects/{project_id}/revisions", tags=["Project Revisions"])


@router.get("", response_model=list[ProjectRevisionRead])
async def list_revisions(project_id: UUID, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    result = await db.execute(
        select(ProjectRevision)
        .where(ProjectRevision.project_id == project_id)
        .order_by(ProjectRevision.revision_number.desc())
    )
    return result.scalars().all()


@router.post("", response_model=ProjectRevisionRead, status_code=status.HTTP_201_CREATED)
async def create_revision(
    project_id: UUID,
    payload: ProjectRevisionCreate,
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        content_hash = snapshot_hash(payload.snapshot)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"Invalid snapshot: {exc}") from exc

    latest = await db.scalar(
        select(func.max(ProjectRevision.revision_number)).where(
            ProjectRevision.project_id == project_id
        )
    )
    revision_number = int(latest or 0) + 1
    parent_id = await db.scalar(
        select(ProjectRevision.id)
        .where(ProjectRevision.project_id == project_id)
        .order_by(ProjectRevision.revision_number.desc())
        .limit(1)
    )

    revision = ProjectRevision(
        project_id=project_id,
        parent_revision_id=parent_id,
        revision_number=revision_number,
        status=RevisionStatus.DRAFT,
        snapshot_hash=content_hash,
        snapshot=payload.snapshot,
        note=payload.note,
        created_by=payload.created_by,
    )
    db.add(revision)
    project.revision = revision_number
    await db.flush()
    await db.refresh(revision)
    return revision


@router.get("/{revision_id}", response_model=ProjectRevisionRead)
async def get_revision(
    project_id: UUID,
    revision_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    revision = await db.scalar(
        select(ProjectRevision).where(
            ProjectRevision.id == revision_id,
            ProjectRevision.project_id == project_id,
        )
    )
    if revision is None:
        raise HTTPException(status_code=404, detail="Revision not found")
    return revision
