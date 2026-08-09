"""FastAPI application — RCC Structural Building Design App.

Entry point: uvicorn backend.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.database import engine, Base

# Import routes
from backend.api.routes import projects, building_input, loads, analysis, design, reports, excel

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle events."""
    # Create tables on startup (dev only — use Alembic migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: dispose engine
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Full-featured RCC structural building design application with OpenSeesPy FEA, BNBC 2020 / ACI 318-19 code compliance, and automated design reporting.",
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


# ── Health Check ─────────────────────────────────────────
@app.get("/api/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
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
