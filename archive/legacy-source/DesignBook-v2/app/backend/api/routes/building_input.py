"""API routes — Building Input (grids, floors, structural members)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.project import GridDefinition, FloorDefinition
from backend.models.member import StructuralMember
from backend.api.schemas.project import (
    GridDefinitionCreate, GridDefinitionRead,
    FloorDefinitionCreate, FloorDefinitionRead,
)
from backend.api.schemas.member import MemberCreate, MemberUpdate, MemberRead

router = APIRouter(prefix="/projects/{project_id}", tags=["Building Input"])


# ── Grids ────────────────────────────────────────────────


@router.get("/grids", response_model=list[GridDefinitionRead])
async def list_grids(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(GridDefinition)
        .where(GridDefinition.project_id == project_id)
        .order_by(GridDefinition.axis, GridDefinition.position_m)
    )
    return result.scalars().all()


@router.post("/grids", response_model=GridDefinitionRead, status_code=201)
async def create_grid(
    project_id: UUID,
    payload: GridDefinitionCreate,
    db: AsyncSession = Depends(get_db),
):
    grid = GridDefinition(project_id=project_id, **payload.model_dump())
    db.add(grid)
    await db.flush()
    await db.refresh(grid)
    return grid


@router.post("/grids/batch", response_model=list[GridDefinitionRead], status_code=201)
async def create_grids_batch(
    project_id: UUID,
    payloads: list[GridDefinitionCreate],
    db: AsyncSession = Depends(get_db),
):
    grids = [GridDefinition(project_id=project_id, **p.model_dump()) for p in payloads]
    db.add_all(grids)
    await db.flush()
    for g in grids:
        await db.refresh(g)
    return grids


# ── Floors ───────────────────────────────────────────────


@router.get("/floors", response_model=list[FloorDefinitionRead])
async def list_floors(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(FloorDefinition)
        .where(FloorDefinition.project_id == project_id)
        .order_by(FloorDefinition.floor_number)
    )
    return result.scalars().all()


@router.post("/floors", response_model=FloorDefinitionRead, status_code=201)
async def create_floor(
    project_id: UUID,
    payload: FloorDefinitionCreate,
    db: AsyncSession = Depends(get_db),
):
    floor = FloorDefinition(project_id=project_id, **payload.model_dump())
    db.add(floor)
    await db.flush()
    await db.refresh(floor)
    return floor


@router.post("/floors/batch", response_model=list[FloorDefinitionRead], status_code=201)
async def create_floors_batch(
    project_id: UUID,
    payloads: list[FloorDefinitionCreate],
    db: AsyncSession = Depends(get_db),
):
    floors = [FloorDefinition(project_id=project_id, **p.model_dump()) for p in payloads]
    db.add_all(floors)
    await db.flush()
    for f in floors:
        await db.refresh(f)
    return floors


# ── Structural Members ───────────────────────────────────


@router.get("/members", response_model=list[MemberRead])
async def list_members(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(StructuralMember)
        .where(StructuralMember.project_id == project_id)
        .order_by(StructuralMember.floor_number, StructuralMember.label)
    )
    return result.scalars().all()


@router.post("/members", response_model=MemberRead, status_code=201)
async def create_member(
    project_id: UUID,
    payload: MemberCreate,
    db: AsyncSession = Depends(get_db),
):
    member = StructuralMember(project_id=project_id, **payload.model_dump())
    db.add(member)
    await db.flush()
    await db.refresh(member)
    return member


@router.patch("/members/{member_id}", response_model=MemberRead)
async def update_member(
    project_id: UUID,
    member_id: UUID,
    payload: MemberUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StructuralMember).where(
            StructuralMember.id == member_id,
            StructuralMember.project_id == project_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(member, field, value)

    await db.flush()
    await db.refresh(member)
    return member


@router.delete("/members/{member_id}", status_code=204)
async def delete_member(
    project_id: UUID,
    member_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StructuralMember).where(
            StructuralMember.id == member_id,
            StructuralMember.project_id == project_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    await db.delete(member)
