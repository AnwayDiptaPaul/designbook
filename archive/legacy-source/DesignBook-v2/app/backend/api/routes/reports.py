"""API routes — Report generation."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.project import Project

router = APIRouter(prefix="/projects/{project_id}", tags=["Reports"])


@router.post("/reports/pdf")
async def generate_pdf_report(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Generate a PDF design report. Stubbed for Phase 1."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # TODO: Phase 8 — call report_generator.py
    return {
        "status": "stub",
        "message": "PDF report generation will be implemented in Phase 8",
        "project_name": project.name,
    }


@router.post("/reports/quantity-takeoff")
async def generate_quantity_takeoff(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Generate quantity takeoff (concrete, rebar, formwork). Stubbed."""
    return {
        "status": "stub",
        "message": "Quantity takeoff will be implemented in Phase 8",
    }


@router.post("/reports/cost-estimate")
async def generate_cost_estimate(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Generate cost estimate using PWD rates. Stubbed."""
    return {
        "status": "stub",
        "message": "Cost estimation will be implemented in Phase 8",
    }
