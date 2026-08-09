# pyre-ignore-all-errors
"""Design endpoints with an explicit release gate.

The maintained snapshot workflow lives under ``backend.engineering``. The
legacy member service is not connected to persisted AnalysisResult records and
must not be exposed as an approved design API.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/projects/{project_id}", tags=["Design"])


def _design_not_released() -> None:
    raise HTTPException(
        status_code=501,
        detail="Member design API is not released; a completed snapshot-bound analysis result is required",
    )


@router.post("/members/{member_id}/design")
async def design_member(project_id: UUID, member_id: UUID):
    _design_not_released()


@router.post("/design-all")
async def design_all_members(project_id: UUID):
    _design_not_released()