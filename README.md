# DesignBook

DesignBook is a prototype for a traceable RCC structural-design workflow for Bangladesh. It combines a FastAPI/OpenSeesPy backend with a React/TypeScript frontend and references the BNBC, PWD, and spreadsheet materials as reference sources (detailed in [doc-files.md](doc-files.md)).

## Current status

The repository is **not production-ready**. It contains promising prototypes for modelling, design, and visualisation, but several critical paths remain prototype or gated: production analysis-worker enablement, progress streaming, time-history analysis, Excel-based verification, and much of the frontend-to-API workflow. Engineering results require independent review and must not be used for construction decisions.

The verified implementation strategy, supported-release boundary, quality gates, target structure, and delivery sequence are in [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md).

## Repository guide

- `app/backend/` — FastAPI API, database models, structural-analysis and design prototypes.
- `app/frontend/` — React/Vite user-interface prototype.
- [doc-files.md](doc-files.md) — Index and description of regulatory PDFs and calculation workbooks (ignored in Git).
- `docs/` — user-facing and technical documentation.
- `skills/` — project-specific guidance that must be reviewed before relevant implementation work.
- `archive/legacy-source/` — compact source-only snapshots of earlier iterations, retained because this workspace has no Git history.

## Development prerequisites

- Python 3.12 (the source declares this target)
- Node.js compatible with the committed frontend lockfile
- PostgreSQL and Redis for the existing persistence/job architecture

Do not rely on historical setup instructions or “verified” status claims without re-running the relevant checks. The initial implementation milestone is a tested, reproducible gravity-frame-to-beam/column-design vertical slice.

## Reference Materials & Machine-Readable Code

The raw PDF and Excel reference files are stored locally under `doc-files/` and are ignored by Git. For an inventory of these files, see [doc-files.md](doc-files.md).

For a structured, machine-readable (AI-ready) version of the Bangladesh National Building Code (BNBC) 2020 (including clauses, tables, and Mermaid flowcharts), please see the [bnbc-2020-database](https://github.com/AnwayDiptaPaul/bnbc-2020-database/) repository.

