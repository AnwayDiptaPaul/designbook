"""API routes — Design endpoints (per-member and design loop)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.member import StructuralMember, MemberStatus
from backend.api.schemas.member import MemberRead

router = APIRouter(prefix="/projects/{project_id}", tags=["Design"])


@router.post("/members/{member_id}/design", response_model=MemberRead)
async def design_member(
    project_id: UUID,
    member_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Design a single structural member (computes reinforcement, checks code).
    Full computation logic is in backend.core.design.* — stubbed for Phase 1."""
    result = await db.execute(
        select(StructuralMember).where(
            StructuralMember.id == member_id,
            StructuralMember.project_id == project_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    member.status = MemberStatus.DESIGNING
    await db.flush()

    # Call the new Design Service
    from backend.core.design.service import StructuralDesignService
    
    # Extract forces (stub for now - in production, get from AnalysisResult)
    forces = member.properties.get("forces", {"Mu": 150.0, "Vu": 50.0, "Pu": 1200.0})
    inputs = {
        "fc": member.concrete_grade_mpa.value,
        "fy": member.steel_grade_mpa.value,
        "width": member.width_mm,
        "depth": member.depth_mm,
        "is_pt": member.properties.get("is_pt", False),
        "span": member.length_mm / 1000 if member.length_mm else 6.0
    }
    
    design_result = StructuralDesignService.design_member(member.member_type, inputs, forces)
    
    member.design_results = design_result
    # Simple pass check: if all statuses are OK
    all_ok = all(res.get("status") == "OK" for res in design_result.values() if isinstance(res, dict))
    member.status = MemberStatus.PASS if all_ok else MemberStatus.FAIL
    
    await db.flush()
    await db.refresh(member)
    return member


@router.post("/design-all", response_model=list[MemberRead])
async def design_all_members(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Design all members in the project (design loop). Stubbed for Phase 1."""
    result = await db.execute(
        select(StructuralMember).where(StructuralMember.project_id == project_id)
    )
    members = result.scalars().all()
    for m in members:
        m.design_results = {
            "status": "stub",
            "message": "Design module not yet implemented — Phase 6",
        }
    await db.flush()
    return members
