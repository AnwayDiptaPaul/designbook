# pyre-ignore-all-errors
"""Isolated persisted analysis worker boundary."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import UUID

from backend.database import async_session_factory
from backend.engineering.analysis_contract import verify_run_config
from backend.engineering.analysis_lifecycle import require_transition
from backend.engineering.service import run_snapshot_analysis
from backend.models.analysis import AnalysisResult, AnalysisRun, AnalysisStatus, AnalysisType
from backend.tasks.celery_app import celery_app


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def _execute_analysis(analysis_run_id: str) -> dict:
    """Execute one immutable run and persist every terminal transition."""

    run_uuid = UUID(str(analysis_run_id))
    async with async_session_factory() as session:
        run = await session.get(AnalysisRun, run_uuid)
        if run is None:
            raise ValueError("analysis run not found")
        if run.status not in {AnalysisStatus.PENDING, AnalysisStatus.RUNNING}:
            return {"analysis_run_id": str(run.id), "status": run.status.value}

        if run.status is AnalysisStatus.PENDING:
            require_transition(run.status, AnalysisStatus.RUNNING)
            run.status = AnalysisStatus.RUNNING
        run.progress_pct = 5
        run.started_at = run.started_at or _utcnow()
        await session.commit()

        try:
            # Cancellation may arrive while the worker is between commits; do
            # not start the solver if the durable state is now terminal.
            await session.refresh(run)
            if run.status is AnalysisStatus.CANCELLED:
                return {"analysis_run_id": str(run.id), "status": run.status.value}
            config = verify_run_config(run.config)
            if run.analysis_type is not AnalysisType.LINEAR_ELASTIC:
                raise ValueError(f"analysis type {run.analysis_type.value} is not released for worker execution")
            report = run_snapshot_analysis(config["snapshot"], config)
            report_data = dict(report.as_dict())
            run.summary = report_data
            run.progress_pct = 100
            require_transition(run.status, AnalysisStatus.COMPLETED)
            run.status = AnalysisStatus.COMPLETED
            run.completed_at = _utcnow()
            for member in report_data.get("members", []):
                session.add(AnalysisResult(
                    analysis_run_id=run.id,
                    member_id=None,
                    result_type="member_design",
                    data=dict(member),
                ))
            await session.commit()
            return {"analysis_run_id": str(run.id), "status": run.status.value, "summary": report_data}
        except Exception as exc:
            require_transition(run.status, AnalysisStatus.FAILED)
            run.status = AnalysisStatus.FAILED
            run.error_message = str(exc)
            run.completed_at = _utcnow()
            run.progress_pct = min(run.progress_pct or 0, 99)
            await session.commit()
            raise


@celery_app.task(bind=True, name="run_analysis")
def run_analysis(self, analysis_run_id: str):
    """Celery entry point; all state changes occur in the database transaction."""

    self.update_state(state="STARTED", meta={"analysis_run_id": analysis_run_id, "progress": 0})
    return asyncio.run(_execute_analysis(analysis_run_id))