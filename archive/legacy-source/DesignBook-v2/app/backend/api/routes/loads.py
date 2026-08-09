"""API routes — Load cases and load combinations."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.load import LoadCase, LoadCombination
from backend.api.schemas.load import (
    LoadCaseCreate, LoadCaseRead,
    LoadCombinationCreate, LoadCombinationRead,
)

router = APIRouter(prefix="/projects/{project_id}", tags=["Loads"])


# ── Load Cases ───────────────────────────────────────────


@router.get("/load-cases", response_model=list[LoadCaseRead])
async def list_load_cases(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LoadCase).where(LoadCase.project_id == project_id)
    )
    return result.scalars().all()


@router.post("/load-cases", response_model=LoadCaseRead, status_code=201)
async def create_load_case(
    project_id: UUID,
    payload: LoadCaseCreate,
    db: AsyncSession = Depends(get_db),
):
    lc = LoadCase(project_id=project_id, **payload.model_dump())
    db.add(lc)
    await db.flush()
    await db.refresh(lc)
    return lc


# ── Load Combinations ───────────────────────────────────


@router.get("/load-combinations", response_model=list[LoadCombinationRead])
async def list_combos(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LoadCombination).where(LoadCombination.project_id == project_id)
    )
    return result.scalars().all()


@router.post("/load-combinations", response_model=LoadCombinationRead, status_code=201)
async def create_combo(
    project_id: UUID,
    payload: LoadCombinationCreate,
    db: AsyncSession = Depends(get_db),
):
    combo = LoadCombination(project_id=project_id, **payload.model_dump())
    db.add(combo)
    await db.flush()
    await db.refresh(combo)
    return combo


@router.post("/load-combinations/generate-standard", response_model=list[LoadCombinationRead], status_code=201)
async def generate_standard_combinations(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Auto-generate ACI 318 / BNBC standard load combinations."""
    from backend.core.combinations.load_combos import get_standard_combinations

    combos_data = get_standard_combinations()
    combos = []
    for cd in combos_data:
        combo = LoadCombination(project_id=project_id, **cd)
        db.add(combo)
        combos.append(combo)

    await db.flush()
    for c in combos:
        await db.refresh(c)
    return combos
