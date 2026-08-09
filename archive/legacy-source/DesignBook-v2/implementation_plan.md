# RCC Structural Building Design App — Implementation Plan

A full-featured, browser-based Reinforced Concrete (RCC) structural engineering application following all directives in [instructions.md](file:///home/garylan/Desktop/Codes/AntiGravity/DesignBook/instructions.md). The app uses a FastAPI backend with OpenSeesPy for finite element analysis, operates against BNBC 2020 and ACI 318-19 codes, and surfaces a premium React + TypeScript frontend with 3D model visualization.

## User Review Required

> [!IMPORTANT]
> This is a large-scope project. We will implement it **phase by phase**, starting with Phase 1 (scaffold + core UI) and progressing through subsequent phases. The entire codebase will live at `/home/garylan/Desktop/Codes/AntiGravity/DesignBook/app/`.

> [!WARNING]
> **OpenSeesPy** must be installed system-wide or in a virtual environment. We will create a `venv` and install all requirements. PostgreSQL and Redis will run in Docker. **Python ≥ 3.11** and **Node.js ≥ 20** are required.

> [!NOTE]
> The initial delivery focuses on a **working, fully navigable frontend shell** with stubbed API responses, plus a working backend skeleton with real endpoints for Projects CRUD, Wind Load, and Seismic ESFM. Full design module backends will be added in follow-up phases.

---

## Proposed Changes

### Project Root
#### [NEW] [docker-compose.yml](file:///home/garylan/Desktop/Codes/AntiGravity/DesignBook/app/docker-compose.yml)
- Services: `api` (FastAPI), `db` (PostgreSQL 16), `redis` (Redis 7), `celery_worker`, `nginx`
- Volumes for PostgreSQL data persistence and static file serving

#### [NEW] [requirements.txt](file:///home/garylan/Desktop/Codes/AntiGravity/DesignBook/app/backend/requirements.txt)
All backend deps: `fastapi`, `uvicorn`, `openseespy`, `numpy`, `scipy`, `openpyxl`, `xlwings`, `reportlab`, `weasyprint`, `pydantic>=2`, `sqlalchemy`, `celery`, `redis`, `matplotlib`, `pandas`, `python-multipart`, `python-jose[cryptography]`, `passlib[bcrypt]`, `asyncpg`, `alembic`

---

### Backend Component

#### [NEW] `app/backend/main.py`
FastAPI app entry point. Registers all routers, CORS, WebSocket for analysis progress.

#### [NEW] `app/backend/database.py`
SQLAlchemy async engine + session factory for PostgreSQL.

#### [NEW] `app/backend/models/` (SQLAlchemy models)
- `project.py` — Project, BuildingInfo, SiteData, GridDefinition
- `member.py` — StructuralMember (polymorphic: beam, column, slab, etc.)
- `load.py` — LoadCase, LoadCombination
- `analysis.py` — AnalysisRun, AnalysisResult

#### [NEW] `app/backend/schemas/` (Pydantic v2)
- `project.py`, `member.py`, `load.py`, `analysis.py`, `design.py`

#### [NEW] `app/backend/api/routes/`
- `projects.py` — CRUD for projects
- `building_input.py` — Grid, floors, member placement
- `loads.py` — DL/LL/Wind/Seismic/Soil load inputs
- `analysis.py` — Trigger analysis (Celery task), WebSocket progress
- `design.py` — Run per-member design, design loop
- `reports.py` — Generate PDF/DOCX/XLSX reports
- `excel.py` — Parse/enhance Excel design sheets

#### [NEW] `app/backend/core/loads/`
- `dead_live.py` — Self-weight auto-compute, SDL, wall loads
- `wind.py` — Full BNBC Part 6 Ch.2: q_z, K_z, K_zt, K_d, G, C_p, C_pi; story forces
- `seismic.py` — ESFM (Z,I,S,Cs,R,W), vertical distribution (F_x, C_vx), RSA, THA hooks

#### [NEW] `app/backend/core/combinations/load_combos.py`
All ACI 318/BNBC strength + serviceability combinations. Envelope generator.

#### [NEW] `app/backend/core/analysis/`
- `opensees_model.py` — Model builder (nodes, beamColumn, shell, springs, BCs)
- `linear_elastic.py` — Gravity + lateral static analysis runner
- `pdelta.py` — P-Delta geometric transformation, stability coefficient θ check
- `response_spectrum.py` — Eigenvalue extraction, modal participation, CQC/SRSS
- `nonlinear_hinge.py` — Pushover with IMK deterioration model

#### [NEW] `app/backend/core/design/`
All 12 member design modules:
- `beam.py` — Flexure (T-beam), shear, torsion, detailing (dev length, splice, cutoffs)
- `column.py` — P-M interaction surface (biaxial), slenderness, magnification, ties/spiral
- `slab_oneway.py`, `slab_twoway.py`, `slab_beamless.py`
- `shear_wall.py`, `retaining_wall.py`
- `footing_isolated.py`, `footing_combined.py`, `footing_raft.py`
- `staircase.py`, `dome.py`

#### [NEW] `app/backend/core/checks/serviceability.py`
Deflection (Branson Ie, long-term λΔ), crack width, story drift, floor vibration.

#### [NEW] `app/backend/core/detailing/rebar_detailing.py`
Auto-generate SVG detailing drawings for all member types.

#### [NEW] `app/backend/core/soil/soil_reaction.py`
Bearing capacity, settlement, Winkler spring stiffness, earth pressure.

#### [NEW] `app/backend/utils/excel_parser.py`
openpyxl-based parser: extract input/output cells, formulas, section structure.

#### [NEW] `app/backend/utils/excel_enhancer.py`
Enhance all 34 design Excel files: dropdowns, conditional formatting, cover sheet, master summary, design loop sheet. Output to `doc-files/design-excel/enhanced/`.

#### [NEW] `app/backend/utils/report_generator.py`
ReportLab PDF generator with all 10 sections per `instructions.md §17.2`.

#### [NEW] `app/backend/tasks/celery_app.py` + `tasks/analysis_tasks.py`
Celery worker for async OpenSeesPy runs; broadcasts progress via Redis pub/sub → WebSocket.

---

### Frontend Component

#### [NEW] React + TypeScript app via Vite at `app/frontend/`
Initialize with: `npm create vite@latest . -- --template react-ts`

#### Design System
- Tailwind CSS v3 + shadcn/ui component library
- Google Fonts: **Inter** (body) + **JetBrains Mono** (code/numbers)
- Color palette: deep navy `#0A0F1E` background, electric blue `#3B82F6` primary, structural green `#10B981` pass, structural red `#EF4444` fail, amber `#F59E0B` warning
- Glassmorphism cards, smooth micro-animations, dark mode default with light toggle

#### [NEW] `app/frontend/src/pages/`
10 pages matching `instructions.md §5.3`:
1. `Dashboard.tsx` — project grid cards, recent activity, quick-start templates
2. `ProjectSetup.tsx` — project info & site data wizard
3. `GeometryInput.tsx` — structural grid/floor/member placement
4. `LoadInput.tsx` — tabbed: DL/LL/Wind/Seismic/Soil
5. `AnalysisControl.tsx` — analysis type select, run button, real-time progress
6. `ResultsViewer.tsx` — 3D deformed shape, force/moment diagrams
7. `DesignModule.tsx` — per-member design view, design loop controls
8. `DetailingDrawings.tsx` — SVG detailing viewer
9. `Reports.tsx` — report config + PDF/DOCX/XLSX download
10. `ExcelManager.tsx` — Excel file browser, enhanced sheet export

#### [NEW] `app/frontend/src/components/`
Key reusable components:
- `Layout/` — Sidebar (project tree), TopToolbar, RightPanel, BottomStatusBar
- `ThreeViewer/` — React Three Fiber 3D building model with orbit controls
- `MemberColorLegend/` — Gray/Blue/Green/Red/Orange status indicators
- `DesignLoopPanel/` — Loop controls, iteration counter, convergence display
- `WindLoadChart/` — Recharts: wind pressure vs. height profile
- `SeismicChart/` — Response spectrum + mode shape animation
- `PMDiagram/` — D3.js P-M interaction diagram for columns
- `ForceEnvelopeChart/` — Moment/shear envelope overlay chart
- `MemberForm/` — Dynamic form per member type using React Hook Form + Zod

#### [NEW] `app/frontend/src/store/`
Zustand stores:
- `projectStore.ts` — current project, building data
- `analysisStore.ts` — analysis state, progress, results
- `designStore.ts` — design results per member
- `uiStore.ts` — selected member, active panel, dark mode, undo/redo stack

#### [NEW] `app/frontend/src/hooks/`
- `useWebSocket.ts` — connects to `/ws/analysis/{task_id}` for real-time progress
- `useProject.ts`, `useAnalysis.ts`, `useDesign.ts` — React Query wrappers

---

### Docker & Deployment

#### [NEW] `app/backend/Dockerfile`
Python 3.11 slim, install requirements, uvicorn entrypoint.

#### [NEW] `app/frontend/Dockerfile`
Node 20 alpine, vite build, nginx serve.

#### [NEW] `app/nginx/nginx.conf`
Reverse proxy: `/api/` → FastAPI, `/` → React SPA, `/ws/` → WebSocket upgrade.

---

## Verification Plan

### Automated Tests
*No existing tests found in the project. We will add basic sanity tests.*

1. **Backend unit tests** — `pytest app/backend/tests/`:
   ```bash
   cd /home/garylan/Desktop/Codes/AntiGravity/DesignBook/app
   python -m pytest backend/tests/ -v
   ```
   Tests cover: wind load calculation (known BNBC inputs/outputs), seismic ESFM base shear, beam flexural design (verify As for a standard beam), load combination envelope.

2. **API smoke test** (FastAPI TestClient):
   ```bash
   cd /home/garylan/Desktop/Codes/AntiGravity/DesignBook/app
   python -m pytest backend/tests/test_api.py -v
   ```

### Manual Verification (Browser)
After running `docker compose up` (or `uvicorn` dev + `npm run dev`):

1. Open `http://localhost:5173` → Dashboard loads with project cards and a "New Project" button
2. Click "New Project" → ProjectSetup wizard opens, fill in all required fields, save
3. Navigate to Geometry Input → define a 5×4 grid (5 bays X, 4 bays Y), 5 stories
4. Navigate to Load Input → input DL=3 kPa, LL=5 kPa (commercial), select Wind Speed=47 m/s, Seismic Zone II
5. Navigate to Analysis Control → click "Run Gravity Analysis" → progress bar shows completion
6. Navigate to Results Viewer → 3D model renders, moment/shear diagrams display for a beam
7. Navigate to Design Module → select a beam, click "Design" → As result shown with pass/fail
8. Navigate to Reports → generate PDF → file downloads
9. Navigate to Excel Manager → "Enhance All" → enhanced files visible in the list

### Dev Server Quick Start (for development)
```bash
# Terminal 1 — Backend
cd /home/garylan/Desktop/Codes/AntiGravity/DesignBook/app
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend
cd /home/garylan/Desktop/Codes/AntiGravity/DesignBook/app/frontend
npm install && npm run dev
```
