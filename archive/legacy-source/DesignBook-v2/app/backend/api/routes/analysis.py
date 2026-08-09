"""API routes — Structural Analysis."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.analysis import AnalysisRun, AnalysisResult, AnalysisStatus
from backend.api.schemas.analysis import AnalysisRunCreate, AnalysisRunRead, AnalysisResultRead

router = APIRouter(prefix="/projects/{project_id}", tags=["Analysis"])


@router.get("/analysis-runs", response_model=list[AnalysisRunRead])
async def list_analysis_runs(project_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AnalysisRun)
        .where(AnalysisRun.project_id == project_id)
        .order_by(AnalysisRun.created_at.desc())
    )
    return result.scalars().all()


@router.post("/analysis-runs", response_model=AnalysisRunRead, status_code=201)
async def create_analysis_run(
    project_id: UUID,
    payload: AnalysisRunCreate,
    db: AsyncSession = Depends(get_db),
):
    run = AnalysisRun(
        project_id=project_id,
        analysis_type=payload.analysis_type,
        config=payload.config,
        status=AnalysisStatus.PENDING,
    )
    db.add(run)

    # Activate actual analysis engine (Phase 5/6 transition)
    from backend.core.analysis.opensees_model import OpenSeesModelBuilder
    
    try:
        builder = OpenSeesModelBuilder()
        builder.initialize_model()
        # Stub: define a simple model for validation
        builder.define_node(1, 0, 0, 0)
        builder.define_node(2, 0, 0, 3.5)
        builder.define_fixity(1, [1,1,1,1,1,1])
        builder.define_geometric_transformation(1, 'Linear', [0, 1, 0])
        builder.define_elastic_beam_column(1, 1, 2, 0.1, 2e7, 1e7, 1e-3, 0.01, 0.01, 1)
        
        if payload.analysis_type.lower() == "static":
            builder.analyze_static(1)
        elif payload.analysis_type.lower() == "modal":
            periods = builder.analyze_modal(3)
            run.config["periods"] = periods
        
        run.status = AnalysisStatus.COMPLETED
    except Exception as e:
        run.status = AnalysisStatus.FAILED
        run.config["error"] = str(e)
        
    await db.flush()
    return run


@router.get("/analysis-runs/{run_id}", response_model=AnalysisRunRead)
async def get_analysis_run(
    project_id: UUID,
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AnalysisRun).where(
            AnalysisRun.id == run_id,
            AnalysisRun.project_id == project_id,
        )
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    return run


@router.get("/analysis-runs/{run_id}/results", response_model=list[AnalysisResultRead])
async def get_analysis_results(
    project_id: UUID,
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AnalysisResult).where(AnalysisResult.analysis_run_id == run_id)
    )
    return result.scalars().all()
