# DesignBook application workspace

This directory contains the current FastAPI/OpenSeesPy backend prototype and
React/Vite frontend prototype. It is governed by the repository-level
[implementation plan](../IMPLEMENTATION_PLAN.md) and the
[capability matrix](../docs/CAPABILITY_MATRIX.md).

## Local prerequisites

- Python 3.11/3.12 (see [venv.md](venv.md) for virtual environment details) with `backend/requirements.txt` installed
- Node.js compatible with `frontend/package-lock.json`
- PostgreSQL and Redis for the existing persistence/job prototypes

Copy `.env.example` to `.env` for local configuration. Do not commit `.env` or
real credentials. Schema creation on application startup is disabled by
default; enable it only for isolated local bootstrap until the Alembic
migration workflow is complete.

## Run locally

```bash
# Backend, from app/
PYTHONPATH=. python -m uvicorn backend.main:app --reload --port 8000

# Frontend, from app/frontend/
npm install
npm run dev
```

The current application is a prototype. Analysis jobs, progress streaming,
Excel parity, and several frontend workflows remain planned or partially
implemented; consult the capability matrix before relying on a feature.
