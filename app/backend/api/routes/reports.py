# pyre-ignore-all-errors
"""API routes for report capabilities that are not yet runtime-enabled."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models.project import Project

router = APIRouter(prefix="/projects/{project_id}", tags=["Reports"])


def _not_implemented(capability: str) -> None:
    raise HTTPException(status_code=501, detail=f"{capability} is not runtime-enabled; no report was generated")


@router.post("/reports/pdf")
async def generate_pdf_report(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Project not found")
    _not_implemented("PDF report generation")


@router.post("/reports/quantity-takeoff")
async def generate_quantity_takeoff(project_id: UUID, db: AsyncSession = Depends(get_db)):
    _not_implemented("Quantity takeoff")


@router.post("/reports/cost-estimate")
async def generate_cost_estimate(project_id: UUID, db: AsyncSession = Depends(get_db)):
    _not_implemented("Cost estimation")