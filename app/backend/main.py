# pyre-ignore-all-errors
"""FastAPI application — RCC Structural Building Design App.

Entry point: uvicorn backend.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.config import get_settings
from backend.database import engine, Base

# Import routes
from backend.api.routes import projects, building_input, loads, analysis, design, reports, excel, revisions
from backend.models.revision import ProjectRevision  # noqa: F401 - register metadata

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle events."""
    # Local bootstrap only. Shared environments must run reviewed migrations
    # before the application starts; see backend/migrations/README.md.
    if settings.CREATE_SCHEMA_ON_STARTUP:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: dispose engine
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "DesignBook structural-design prototype. Supported calculations and "
        "validation status are exposed explicitly; results require engineering review."
    ),
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register API routers ─────────────────────────────────
app.include_router(projects.router, prefix="/api")
app.include_router(building_input.router, prefix="/api")
app.include_router(loads.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(design.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(excel.router, prefix="/api")
app.include_router(revisions.router, prefix="/api")


# ── Health Check ─────────────────────────────────────────
@app.get("/api/health", tags=["System"])
async def health_check():
    """Liveness endpoint that does not require database connectivity."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/api/ready", tags=["System"])
async def readiness_check():
    """Readiness endpoint for deployment probes and operator diagnostics."""

    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "dependency": "database", "error": "database unavailable"},
        )
    return {"status": "ready", "dependencies": {"database": "ok"}}


@app.get("/api/capabilities", tags=["System"])
async def capabilities():
    """Return an explicit capability boundary for clients and reviewers."""

    return {
        "status": "prototype",
        "calculation_status": "engineering_review_required",
        "released": ["project_crud", "input_validation", "reference_data_inventory"],
        "prototype": ["linear_analysis", "member_design", "report_generation", "opt_in_persisted_analysis_worker"],
        "planned": ["production_worker_enablement", "lateral_loads", "workbook_parity"],
    }


# ── WebSocket for analysis progress (Phase 5 — live) ────
@app.websocket("/ws/analysis/{task_id}")
async def analysis_progress_ws(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for real-time analysis progress updates.
    Phase 5 will implement Redis pub/sub → WebSocket streaming."""
    await websocket.accept()
    try:
        await websocket.send_json({
            "task_id": task_id,
            "status": "stub",
            "message": "WebSocket progress streaming — Phase 5",
            "progress": 0,
        })
        # Keep connection open (in Phase 5, will listen to Redis channel)
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
