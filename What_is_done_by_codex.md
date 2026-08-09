# Detailed Codex Execution Summary: DesignBook Project

This document provides a highly detailed, technically precise summary of the codebase updates, files modified/added, dependency blocks, cleanup operations, and incomplete tasks left by Codex. It serves as a transition record and reference guide for ongoing development.

---

## 1. Added files & Modules (In-Depth)

Codex implemented the core components of the **Phase 0 (Foundation Reset)** and **Phase 1 (Revision Lifecycle)** milestones. The added components are structured as follows:

### 1.1 Engineering Domain Primitives (`app/backend/domain/`)
*   **[units.py](file:///g:/AI/Works/DesignBook/app/backend/domain/units.py)**: Establishes a strict SI unit system boundary. It defines a frozen `Quantity` dataclass (storing `value: float` and `unit: str`) and validates that values are finite and units exist in the conversion map.
    *   *Supported units*: Length (`m`, `mm`), Force (`kN`, `N`), Pressure (`kPa`, `Pa`, `MPa`), Force-per-length (`kN/m`), Force-per-area (`kN/m²`), and Moment (`kN·m`).
    *   *Validation*: Includes `ensure_positive()` helper to throw exceptions for negative or non-finite inputs.
*   **[snapshots.py](file:///g:/AI/Works/DesignBook/app/backend/domain/snapshots.py)**: Handles immutable snapshot generation for project configurations.
    *   *JSON Canonicalization*: Uses `json.dumps()` with sorted keys (`sort_keys=True`), no whitespace (`separators=(",", ":")`), and strictly finite floats (`allow_nan=False`) to guarantee identical string outputs for matching data.
    *   *Hashing*: Implements `snapshot_hash()` which generates a SHA-256 hex digest of the canonical JSON string, representing a unique signature for any set of project inputs.

### 1.2 Database Schema & Models (`app/backend/models/`)
*   **[revision.py](file:///g:/AI/Works/DesignBook/app/backend/models/revision.py)**: Implements the database table `project_revisions` to record project snapshots.
    *   *Status State*: Defs `RevisionStatus` Enum (`draft`, `frozen`, `superseded`).
    *   *Relationships*: Establishes relationships from `ProjectRevision` to `Project` (back-populated to `revisions`), parent revision (remote_side self-reference), and `AnalysisRun` (back-populated to `revision`).
    *   *Columns*: Stores revision index (`revision_number`), SHA-256 hash (`snapshot_hash`), and the full input dictionary (`snapshot` JSON column).
*   **Analysis Run Association (`app/backend/models/analysis.py`)**: Modified `AnalysisRun` ORM model to link to the corresponding project revision:
    *   `revision_id = Column(UUID(as_uuid=True), ForeignKey("project_revisions.id", ondelete="SET NULL"), nullable=True)`
    *   `revision = relationship("ProjectRevision", back_populates="analysis_runs")`

### 1.3 API Routes & Contracts (`app/backend/api/`)
*   **[revisions.py Routes](file:///g:/AI/Works/DesignBook/app/backend/api/routes/revisions.py)**: Added REST endpoints mounted under `/projects/{project_id}/revisions` for handling revisions:
    *   `GET /`: Fetches all revisions of a project ordered descending by revision number.
    *   `POST /`: Creates a new revision. Generates the snapshot hash, retrieves the previous revision to assign `parent_revision_id`, increments the revision number, updates the primary `Project.revision` field, and persists the draft.
    *   `GET /{revision_id}`: Retrieves a specific project revision.
*   **[revision.py Schemas](file:///g:/AI/Works/DesignBook/app/backend/api/schemas/revision.py)**: Added Pydantic v2 schemas:
    *   `ProjectRevisionCreate`: Accepts inputs for `snapshot: dict`, optional `note: str`, and optional author name `created_by: str`.
    *   `ProjectRevisionRead`: Complete representation of the revision containing UUIDs, dates (`created_at`, optional `frozen_at`), hashes, and values. Includes `from_attributes = True` for SQLAlchemy ORM conversion.

### 1.4 Diagnostic & Readiness Checks
*   **Readiness Check (`/api/ready` in `main.py`)**: Added a database-aware endpoint that runs a quick `SELECT 1` query to test PostgreSQL connectivity. Returns a `503 Service Unavailable` with details if the database is down.
*   **Capabilities Boundary (`/api/capabilities` in `main.py`)**: Exposes arrays defining what features are `released` (production ready), `prototype` (opt-in/experimental), and `planned` (not yet implemented) to prevent false assumptions of certified status.
*   **`CAPABILITY_MATRIX.md`**: Documented calculation parity, verification status, and manual spreadsheet dependencies.

---

## 2. Hardened Constraints & Validations (Modified)

Codex tightened validation across existing files to prevent bad geometries or unsafe setups from reaching calculation solvers:

### 2.1 Pydantic Request Validation (`app/backend/api/schemas/project.py`)
*   **Building Constraints (`BuildingInfoBase`)**: Added limit guards:
    *   `num_basements` restricted between `0` and `20`.
    *   `num_ground_floors` restricted between `1` and `10`.
    *   `num_typical_floors` restricted between `0` and `200`.
    *   `num_penthouse_floors` restricted between `0` and `20`.
    *   `total_height_m` bounded from `0` to `1000`.
*   **Location Coordinates (`SiteDataBase`)**: Added a post-model validator `validate_coordinates()` checking that `latitude` and `longitude` are either both populated or both null. Bounded basic wind speed between `0` and `150` m/s.
*   **Grid Axis RegEx (`GridDefinitionBase`)**: Bounded positions and added validation constraint checking that the grid axis is exactly `X` or `Y` (`pattern=r"^[XY]$"`).
*   **Floor Limits (`FloorDefinitionBase`)**: Enforced floor numbers from `-20` to `300`, floor heights strictly positive up to `100` m.

### 2.2 System & Startup Gating (`app/backend/config.py` & `main.py`)
*   **Lifespan Management**: Migrated DB creation. If `CREATE_SCHEMA_ON_STARTUP` is true, SQL schema initialization uses `Base.metadata.create_all` safely inside the lifespan.
*   **Security Gating (`validate_environment_safety()`)**: Throws validation errors if `ENVIRONMENT` is `staging` or `production` but the `SECRET_KEY` is empty/default, or if `DEBUG` or `CREATE_SCHEMA_ON_STARTUP` is set to True.
*   **Config Gating (`ENABLE_ANALYSIS_EXECUTION`)**: Added a config flag to explicitly gate experimental OpenSeesPy execution until workers are fully isolated.

---

## 3. Irreversible Cleanup (Removed)

Due to the absence of active Git history in the workspace, Codex performed a thorough, permanent deletion of obsolete files and libraries after obtaining user approval:
1.  **`previous-works/`**: Cleaned up the 394.95 MB folder containing unversioned source copies.
2.  **`archive/legacy-source`**: Substituted the above with a compact source-only compressed legacy zip file (~1.32 MB) containing code files for archival reference.
3.  **`app/frontend/node_modules/`**: Deleted the 239.95 MB node dependencies folder to allow a clean, reproducible installation.
4.  **`app/frontend/dist/`**: Deleted Vite production build directory.
5.  **Obsolete Docs & Configs**: Deleted root `.env` (contained only PYTHONPATH), `obsolete implementation_plan.md`, `docs/plan.md`, `docs/fix.md`, `docs/checking.md`, and the stale `pyright_errors.txt` log.
6.  **Bytecode & Caches**: Cleared all `__pycache__` folders and generated PDF test reports.

---

## 4. Could Not Be Completed & Blockers

Codex ran out of runtime credits while working on the versioned standards registry and load combinations engine, leaving the following blockers:

### 4.1 Dependency Installation Blockers
*   **Frontend Vite Build Blocked**: Running `npm install` fails/stalls because of a broken dependency tree. Specifically, the lockfile references a native binding for `Rolldown` (Vite's next-gen bundler) that is unavailable in the execution environment.
*   **Backend Import Blocker**: Running the backend locally yields `ImportError` because `pydantic-settings` is missing from the environment.

### 4.2 Interrupted Milestone (Standards Registry & Combinations)
*   **Standards Registry**: A versioned standards metadata store is defined in `app/backend/engineering/codes/registry.py` with static reference maps to `BNBC 2020` and `ACI 318-19` loads, but the logic is a static shell. The dynamic selection of codes, load-factor query methods, and database persistence/seeding for code releases were left incomplete.
*   **Load Combinations**: The calculations in `app/backend/core/combinations/load_combos.py` and `app/backend/engineering/loads/combinations.py` are stubs that need to be unified with the new `registry.py` metadata model.

---

## 5. Remaining Milestone Tasks

According to the V1 Roadmap in `IMPLEMENTATION_PLAN.md`, the next execution priorities are:
1.  **Resolve Frontend Bindings**: Clean and update `app/frontend/package.json` to use stable, platform-agnostic Vite bundler setups and verify a successful build.
2.  **Alembic Setup**: Bootstrap Alembic in `app/backend/migrations/` and replace `CREATE_SCHEMA_ON_STARTUP` with structured SQL migration histories.
3.  **Complete the Code-Data Registry**: Write the seeding logic for BNBC 2020 load factors, and provide query routes (`GET /api/reference-data/releases`) to the client.
4.  **Isolate OpenSees Solver**: Refactor `opensees_model.py` to strip out domain details, and write the subprocess boundary runner to keep the FastAPI server safe from solver memory leaks or crashes.
