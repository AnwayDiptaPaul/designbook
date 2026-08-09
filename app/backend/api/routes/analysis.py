# pyre-ignore-all-errors
"""API routes for analysis-run records and explicitly gated execution."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.config import get_settings
from backend.database import get_db
from backend.models.analysis import AnalysisRun, AnalysisResult, AnalysisStatus
from backend.models.project import Project
from backend.engineering.service import run_snapshot_analysis
from backend.engineering.analysis_lifecycle import require_transition
from backend.engineering.analysis_contract import prepare_run_config
from backend.api.schemas.analysis import AnalysisRunCreate, AnalysisRunRead, AnalysisResultRead
from backend.tasks.analysis_tasks import run_analysis

router = APIRouter(prefix="/projects/{project_id}", tags=["Analysis"])
settings = get_settings()


@router.get("/analysis-runs", response_model=list[AnalysisRunRead])
async def list_analysis_runs(project_id: UUID, db: AsyncSession = Depends(get_db)):
    project_result = await db.execute(select(Project.id).where(Project.id == project_id))
    if project_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Project not found")
    result = await db.execute(select(AnalysisRun).where(AnalysisRun.project_id == project_id).order_by(AnalysisRun.created_at.desc()))
    return result.scalars().all()


@router.post("/analysis-runs", response_model=AnalysisRunRead, status_code=201)
async def create_analysis_run(project_id: UUID, payload: AnalysisRunCreate, db: AsyncSession = Depends(get_db)):
    if not settings.ENABLE_ANALYSIS_EXECUTION:
        raise HTTPException(status_code=501, detail="Analysis execution is not runtime-enabled; no run was created")
    project_result = await db.execute(select(Project.id).where(Project.id == project_id))
    if project_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        prepared_config = prepare_run_config(payload.config)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    run = AnalysisRun(
        project_id=project_id,
        analysis_type=payload.analysis_type,
        status=AnalysisStatus.PENDING,
        progress_pct=0,
        config=prepared_config,
    )
    db.add(run)
    await db.flush()
    await db.commit()  # enqueue only after the immutable run is durable
    try:
        task = run_analysis.delay(str(run.id))
    except Exception as exc:
        run.status = AnalysisStatus.FAILED
        run.error_message = "analysis queue unavailable"
        await db.commit()
        raise HTTPException(status_code=503, detail="Analysis queue is unavailable; run marked failed") from exc
    run.celery_task_id = str(task.id)
    await db.commit()
    await db.refresh(run)
    return run


@router.post("/analysis-preview")
async def preview_analysis(project_id: UUID, payload: AnalysisRunCreate, db: AsyncSession = Depends(get_db)):
    project_result = await db.execute(select(Project.id).where(Project.id == project_id))
    if project_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Project not found")
    snapshot = payload.config.get("snapshot")
    configuration = payload.config.get("configuration", payload.config)
    try:
        return run_snapshot_analysis(snapshot, configuration).as_dict()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/analysis-runs/{run_id}/cancel", response_model=AnalysisRunRead)
async def cancel_analysis_run(project_id: UUID, run_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AnalysisRun).where(AnalysisRun.id == run_id, AnalysisRun.project_id == project_id))
    run = result.scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    if run.status in {AnalysisStatus.COMPLETED, AnalysisStatus.FAILED, AnalysisStatus.CANCELLED}:
        raise HTTPException(status_code=409, detail=f"Analysis run is already terminal: {run.status.value}")
    require_transition(run.status, AnalysisStatus.CANCELLED)
    run.status = AnalysisStatus.CANCELLED
    run.error_message = "cancelled by user"
    await db.commit()
    await db.refresh(run)
    return run

@router.post("/analysis-runs/{run_id}/retry", response_model=AnalysisRunRead, status_code=201)
async def retry_analysis_run(project_id: UUID, run_id: UUID, db: AsyncSession = Depends(get_db)):
    if not settings.ENABLE_ANALYSIS_EXECUTION:
        raise HTTPException(status_code=501, detail="Analysis execution is not runtime-enabled; no retry was created")
    result = await db.execute(select(AnalysisRun).where(AnalysisRun.id == run_id, AnalysisRun.project_id == project_id))
    source = result.scalar_one_or_none()
    if source is None:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    if source.status is not AnalysisStatus.FAILED:
        raise HTTPException(status_code=409, detail="Only failed analysis runs can be retried")
    retry = AnalysisRun(
        project_id=source.project_id,
        revision_id=source.revision_id,
        analysis_type=source.analysis_type,
        status=AnalysisStatus.PENDING,
        progress_pct=0,
        config=dict(source.config),
    )
    db.add(retry)
    await db.flush()
    await db.commit()
    try:
        task = run_analysis.delay(str(retry.id))
    except Exception as exc:
        retry.status = AnalysisStatus.FAILED
        retry.error_message = "analysis queue unavailable"
        await db.commit()
        raise HTTPException(status_code=503, detail="Analysis queue is unavailable; retry marked failed") from exc
    retry.celery_task_id = str(task.id)
    await db.commit()
    await db.refresh(retry)
    return retry

@router.get("/analysis-runs/{run_id}", response_model=AnalysisRunRead)
async def get_analysis_run(project_id: UUID, run_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AnalysisRun).where(AnalysisRun.id == run_id, AnalysisRun.project_id == project_id))
    run = result.scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    return run


@router.get("/analysis-runs/{run_id}/results", response_model=list[AnalysisResultRead])
async def get_analysis_results(project_id: UUID, run_id: UUID, db: AsyncSession = Depends(get_db)):
    run_result = await db.execute(select(AnalysisRun.id).where(AnalysisRun.id == run_id, AnalysisRun.project_id == project_id))
    if run_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    result = await db.execute(select(AnalysisResult).where(AnalysisResult.analysis_run_id == run_id))
    return result.scalars().all()