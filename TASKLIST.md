# DesignBook — Comprehensive Task List

> **Generated**: 2026-08-09 | **Source**: IMPLEMENTATION_PLAN.md, Codex progress log, full codebase audit
>
> **Legend**: `[x]` Done · `[/]` Partially done (prototype exists) · `[ ]` Not started

---

## Status Summary

| Phase | Description | Status |
|---|---|---|
| Phase 0 | Foundation reset & delivery controls | **~60% done by Codex** |
| Phase 1 | Contracts, migrations, revision lifecycle | **~30% done** |
| Phase 2 | Geometry, loads, combinations, fixtures | **~20% prototyped** |
| Phase 3 | Verified gravity-analysis vertical slice | **~15% prototyped** |
| Phase 4 | Initial member design: beams & columns | **~10% prototyped** |
| Phase 5 | Usable frontend vertical slice | **~15% prototyped** |
| Phase 6 | Durable jobs, progress, results lifecycle | **~5% stub** |
| Phase 7 | Lateral loads & structural checks | **~10% prototyped** |
| Phase 8 | Member-family expansion & design loops | **~10% prototyped** |
| Phase 9 | Detailing, QTO, costing, report artifacts | **~5% prototyped** |
| Phase 10 | Production readiness & controlled rollout | **Not started** |

---

## What Codex Completed

1. Created IMPLEMENTATION_PLAN.md (607-line grand plan)
2. Updated README.md to mark prototype status
3. Cleaned workspace (removed previous-works/, node_modules/, build outputs, caches)
4. Created compact legacy archive at archive/legacy-source/
5. Preserved all 16 regulatory PDFs and 34 engineering workbooks
6. Created domain primitives: units.py, snapshots.py
7. Created 6 domain tests in test_domain.py
8. Hardened config.py (env-aware validation, migration-gated schema)
9. Added /api/ready and /api/capabilities endpoints in main.py
10. Hardened project/site/grid/floor validation in project.py
11. Added .env.example
12. Created Revision ORM model in models/revision.py
13. Created Revision API schemas in schemas/revision.py
14. Created Revision routes (GET/POST) in routes/revisions.py
15. Implemented deterministic SHA-256 snapshot hashing
16. Started versioned codes registry in engineering/codes/registry.py
17. Ran out of Codex credits mid-way through standards registry + load-combination engine

---

## Phase 0 — Foundation Reset & Delivery Controls

### 0.1 Repository & Environment Setup
- [x] Add `.env.example` with documented variables
- [x] Move secrets out of defaults (SECRET_KEY validated)
- [/] Document local, test, staging, production configuration (`.env.example` exists but not full docs)
- [x] Fix `.gitignore` (updated by Codex)
- [ ] Add license decision file (LICENSE)
- [ ] Add CODEOWNERS / reviewer map
- [ ] Add `.editorconfig`
- [/] Formatter/linter/type-check configuration (`.pyre_configuration` exists, ESLint config exists, but not unified)
- [/] Dependency manifests (`requirements.txt` dependencies successfully installed in `.venv` via `uv` ✅, `package.json` exists but lockfile/install is currently blocked)

### 0.2 CI Pipeline
- [ ] Create CI job: backend syntax/lint/type checks
- [ ] Create CI job: backend unit tests
- [ ] Create CI job: frontend install/lint/build
- [ ] Create CI job: frontend component tests
- [ ] Create CI job: dependency scan
- [ ] Create CI job: artifact retention
- [ ] Create CI job: security/license/SBOM scan

### 0.3 Architecture Decision Records
- [ ] ADR: Application architecture (layered domain model)
- [ ] ADR: Data snapshots and immutability
- [ ] ADR: Worker isolation strategy
- [ ] ADR: Unit system policy (SI internally)
- [ ] ADR: Standard/version selection model
- [ ] ADR: Storage strategy (files, artifacts)
- [ ] ADR: Authentication approach

### 0.4 Capability Matrix & Status Rewrite
- [x] Create capability matrix (CAPABILITY_MATRIX.md referenced by Codex)
- [x] /api/capabilities endpoint returns explicit scope
- [ ] Rewrite ALL frontend UI wording from implied "verified" to prototype/released status
- [ ] Add "Prototype / Not certified" labels to every unvalidated calculation screen

### 0.5 Test Consolidation
- [ ] Consolidate manual stress scripts into `tests/legacy/` backlog
- [/] Tests exist (25 test files) but many are untriaged prototype tests
- [ ] Create test fixture packages for benchmark scenarios

### 0.6 Dependency Installation Validation
- [x] Validate clean `pip install` from `requirements.txt` (Successfully created `app/.venv` and installed all 68 packages using `uv` ✅)
- [ ] Fix frontend `package-lock.json` (broken Rolldown native binding)
- [ ] Validate clean `npm install` from lockfile
- [ ] Validate `npm run build` succeeds
- [ ] Document exact Node.js version requirement

---

## Phase 1 — Contracts, Migrations & Project Revision Lifecycle

### 1.1 Domain Contracts (Pydantic v2 DTOs)
- [x] Unit system value objects (Quantity, UnitSystem, conversions)
- [x] Snapshot hash value object (canonical_json, snapshot_hash)
- [/] Material DTOs (partial — in schemas but not full Pydantic v2)
- [/] Geometry DTOs (partial — grid/storey in project schemas)
- [/] Member DTOs (partial — member.py schema exists)
- [/] Load DTOs (partial — load.py schema exists)
- [ ] Combination selection DTOs
- [ ] Analysis settings DTOs
- [/] Result message DTOs (partial — analysis.py schema exists)
- [ ] Pagination/error envelope contracts
- [ ] Code selection DTOs with version/edition

### 1.2 Shared Contract Workflow
- [ ] Replace duplicated frontend/backend types with OpenAPI code generation
- [ ] OR implement managed shared-contract workflow
- [/] Frontend types exist (project.ts) but diverge from backend

### 1.3 Database & Migrations
- [/] PostgreSQL schema design (models exist: project, member, load, analysis, revision)
- [ ] Create initial Alembic migration (migrations dir exists but only has README)
- [ ] Seed development code-data release
- [ ] Add transactional repository layer
- [ ] Remove runtime `create_all` (currently behind feature flag, but still present)
- [ ] Test migration forward from empty state

### 1.4 Project CRUD & Revision Lifecycle
- [/] Project CRUD API (projects.py route exists)
- [x] Revision creation API (GET/POST revisions)
- [ ] Revision clone / revert
- [ ] Draft autosave
- [ ] Revision diff (compare two revisions)
- [ ] Soft-delete
- [ ] Audit-event recording per mutation
- [ ] Access checks / authenticated actor identification

### 1.5 API Contract Tests
- [ ] API contract tests for all mutation endpoints
- [ ] Idempotency handling
- [ ] Concurrency / optimistic locking handling
- [/] Some API safety tests exist (test_api_safety.py)

---

## Phase 2 — Geometry, Loads, Combinations & First Fixtures

### 2.1 Building Model Schemas
- [/] Grid definition (exists in project.py schemas)
- [/] Storey definition (exists but needs topology validation)
- [/] Member schemas (exists in member.py)
- [ ] Support schemas with boundary condition types
- [ ] Topology validation (no duplicate members, connected graph, valid grid references)
- [ ] Member local-axis conventions (documented, not enforced)
- [ ] Material assignment validation
- [ ] SI dimensional validation on all geometry inputs

### 2.2 Load Input Implementation
- [/] Self-weight computation (prototype in dead_live.py)
- [/] Superimposed dead load (prototype exists)
- [/] Live load per occupancy (prototype exists)
- [ ] Wall/line load on beams with audit trace
- [ ] Point load input
- [ ] Tributary-area allocation with audit trace
- [ ] Load input validation against SI units

### 2.3 Load Combinations
- [x] Combination catalogue with code/version reference (registry.py — U1-U7, S1-S4)
- [x] Combination identifiers, factors, and category (strength/serviceability)
- [/] Printable explanations (reference metadata exists but not formatted)
- [/] Load combo module in core (load_combos.py)
- [/] Engineering loads module (combinations.py, envelopes.py)
- [/] Tests exist (test_combinations.py, test_envelopes.py)

### 2.4 Test Fixture Packages
- [ ] Small portal frame fixture (input JSON + expected results)
- [ ] Two-storey frame fixture
- [ ] Regular mid-rise frame fixture
- [ ] Hand-calculated self-weight verification
- [ ] Hand-calculated load-combination verification

### 2.5 Results Contracts
- [/] Forces contract (partial in analysis_contract.py)
- [ ] Displacements contract (solver-neutral)
- [ ] Reactions contract (solver-neutral)
- [ ] Combination envelope contract
- [ ] Warnings / failure diagnostics contract
- [ ] All contracts independent of OpenSeesPy return formats

---

## Phase 3 — Verified Gravity-Analysis Vertical Slice

### 3.1 Solver-Neutral Structural Model
- [/] StructuralModel abstraction (partial — opensees_model.py is 36KB but tightly coupled)
- [ ] Strict OpenSees model adapter (clean separation from domain)
- [ ] Solver-neutral result types

### 3.2 OpenSees Model Operations
- [/] Node creation from grid/storey (prototype in opensees_model.py)
- [/] Element creation (beams, columns) (prototype exists)
- [/] Material/section creation (prototype exists)
- [/] Support boundary conditions (prototype exists)
- [/] Gravity load patterns (prototype exists)
- [/] Static solve execution (prototype exists)
- [/] Force/reaction/displacement extraction (prototype exists)
- [ ] Unconditional cleanup (wipe) after every run

### 3.3 Worker Isolation
- [/] Celery task structure (analysis_tasks.py, celery_app.py)
- [ ] Run solver in a child process (not just Celery worker)
- [ ] Timeout enforcement per run
- [ ] Memory/time metrics collection
- [ ] Cancellation hooks
- [ ] Structured error normalization (no raw OpenSees exceptions)
- [ ] No fallback mock results on failure
- [/] Execution gating via ENABLE_ANALYSIS_EXECUTION flag (exists in config)

### 3.4 Benchmark & Validation
- [/] Gravity frame benchmark test exists (test_gravity_frame_benchmark.py)
- [ ] Compare results to reviewed hand calculations
- [ ] Compare to at least one approved external model benchmark
- [ ] Document acceptance tolerances
- [ ] At least two benchmark models pass acceptance

### 3.5 Result Publishing
- [ ] Result tables with load-case/combo provenance
- [ ] Warnings attached to results
- [ ] Numerical units on every output value
- [ ] Immutable input snapshot linked to every result
- [ ] Solver metadata (version, timing) stored with results

---

## Phase 4 — Initial Member Design: Beams & Columns

### 4.1 Design Requirements Specification
- [ ] Beam design requirements document (accepted limits, failure modes, code clauses)
- [ ] Column design requirements document
- [ ] Material assumptions documented with reviewers

### 4.2 Beam Design Calculator
- [/] Beam flexural design (beam.py — 3.5KB prototype)
- [ ] Refactor into pure typed functions with inputs/outputs
- [ ] Flexure: required As, stress block iteration, rho_min/rho_max checks
- [ ] Shear: Vc, stirrup design, Av/s, max spacing
- [ ] Torsion design (if threshold exceeded)
- [ ] Dimensional tests for all calculations
- [ ] T-beam effect for slab in compression

### 4.3 Column Design Calculator
- [/] Column interaction logic (column.py — 11.8KB prototype)
- [ ] Refactor into pure typed functions
- [ ] Slenderness classification and moment magnification
- [ ] P-M interaction diagram (biaxial)
- [ ] Tie/spiral transverse reinforcement per ACI 25.7
- [ ] Dimensional tests

### 4.4 Calculation Traces
- [ ] Trace data structure: inputs, intermediates, equations/clauses, capacities, demands, utilization, status
- [ ] Governing case identification
- [ ] Messages and warnings per check
- [ ] Every status traceable to governing demand + code source

### 4.5 Design Verification
- [ ] Workbook-parity fixtures (compare to original Excel sheets)
- [ ] Hand-calculation fixtures with tolerance rationale
- [ ] Regression tests for beam examples
- [ ] Regression tests for column examples
- [ ] Invalid/out-of-scope cases refused or flagged

### 4.6 Detailing Data
- [/] Rebar detailing module (detailing.py — 8.2KB prototype)
- [ ] Structured rebar data (bar marks, sizes, counts, spacing)
- [ ] Bar cutoff locations
- [ ] Development lengths (straight, hooked)
- [ ] Splice lengths
- [ ] No construction drawings yet — data only

---

## Phase 5 — Usable Frontend Vertical Slice

### 5.1 App Shell & Infrastructure
- [/] Router / page structure (App.tsx exists)
- [ ] Authentication boundary / route guards
- [ ] Loading / error / empty states (global)
- [ ] Global API error handling
- [ ] Accessible design-system baseline (semantic HTML, ARIA, focus management)
- [ ] Dark/light mode toggle

### 5.2 Dashboard
- [/] Dashboard page exists (Dashboard.tsx — 7.7KB)
- [ ] Replace demo cards with actual project/revision data
- [ ] Show recent actual runs (not mock)
- [ ] Show real warnings and clear status indicators
- [ ] Remove ALL mock/demo data

### 5.3 Project & Model Editor
- [/] Project setup page (ProjectSetup.tsx — 7.5KB)
- [/] Grid/storey editor (BuildingGeometry.tsx, GeometryInput.tsx)
- [/] Member editor (StructuralMembers.tsx — 9.6KB)
- [ ] Material/site assumptions editor with typed forms
- [ ] Server-side validation integration (not just client-side)
- [ ] Form state backed by server (not local-only Zustand)

### 5.4 Load Case Editor
- [/] Load input page (LoadInput.tsx — 14.7KB)
- [ ] Wire to actual backend load APIs
- [ ] Typed forms with Zod validation
- [ ] Server validation feedback display

### 5.5 Visualization
- [/] Three.js viewer exists (ThreeViewer.tsx — 1.3KB stub)
- [ ] 2D model view derived from persisted geometry (priority before 3D)
- [ ] 3D visualization (only after 2D editor is trustworthy)
- [ ] Geometry derived solely from persisted/draft data

### 5.6 Analysis & Design Screens
- [/] Analysis control page (AnalysisControl.tsx — 12.7KB)
- [/] Design module page (DesignModule.tsx — 1.8KB stub)
- [/] Results viewer (ResultsViewer.tsx — 1.2KB stub)
- [ ] Job progress display from real events
- [ ] Result tables with member selection
- [ ] Beam/column design inspection view

### 5.7 Reports Screen
- [/] Reports page (Reports.tsx — 7.8KB)
- [ ] Wire to actual artifact generation API

### 5.8 Testing
- [ ] End-to-end browser tests for full user journey
- [ ] Accessibility tests (fields, errors, focus order, keyboard)
- [/] Frontend safety tests exist (test_frontend_safety.py — backend checking frontend)

---

## Phase 6 — Durable Jobs, Progress & Results Lifecycle

### 6.1 Job State Machine
- [/] Celery task structure exists (analysis_tasks.py)
- [/] Job lifecycle module (analysis_lifecycle.py)
- [ ] Replace placeholder Celery jobs with database-backed execution
- [ ] Implement full state machine: draft > queued > validating > building > solving > extracting > completed
- [ ] Failed state from any processing stage
- [ ] Cancellation flow: cancellation_requested > cancelled
- [ ] Superseded state for newer revisions
- [ ] All transitions persisted as events

### 6.2 Progress Streaming
- [/] WebSocket endpoint exists (main.py line 109) — stub only
- [ ] Persist job events to database
- [ ] Stream events over WebSocket/SSE
- [ ] Polling fallback
- [ ] Reconnect semantics
- [ ] Authorization on WebSocket connections
- [ ] Back-pressure handling

### 6.3 Safety & Recovery
- [ ] Cancellation at safe solver boundaries
- [ ] Timeout enforcement per job
- [ ] Retry classification (transient vs permanent failure)
- [ ] Duplicate-job guards
- [ ] Dead-letter / error investigation workflow
- [ ] Process restart recovery (resume, mark interrupted, or require retry)

### 6.4 Observability
- [ ] Latency metrics per job phase
- [ ] Memory usage tracking
- [ ] Run size metrics
- [ ] Queue depth monitoring
- [ ] Error classification metrics
- [ ] Benchmark metrics

### 6.5 Operator Tools
- [ ] Operator diagnostics UI or protected endpoints
- [ ] Retention/cleanup policy for old jobs
- [ ] Alert thresholds

---

## Phase 7 — Lateral Loads & Structural Checks

### 7.1 BNBC Wind Loads
- [/] Wind load module (wind.py — 7KB prototype)
- [ ] Input/exposure validation per BNBC
- [ ] Velocity pressure (q_z) per floor
- [ ] K_z, K_zt, K_d coefficients with code references
- [ ] Gust factor (rigid/flexible)
- [ ] External/internal pressure coefficients (C_p, C_pi)
- [ ] Floor force distribution
- [ ] Base shear and overturning moment
- [ ] Governing wind cases (X+, X-, Y+, Y-)
- [ ] Engineering requirements document
- [ ] Benchmark suite with code citations

### 7.2 BNBC Equivalent-Static Seismic
- [/] Seismic load module (seismic.py — 8.3KB prototype)
- [ ] Zone/site/importance/system parameter validation
- [ ] Seismic weight computation
- [ ] Period treatment (empirical, analytical)
- [ ] Base shear calculation with all factors
- [ ] Vertical distribution (C_vx)
- [ ] Directional cases
- [ ] Engineering requirements document
- [ ] Benchmark suite

### 7.3 Linear Lateral Analysis
- [/] Linear elastic solver (linear_elastic.py — 2.6KB)
- [ ] Storey displacement extraction
- [ ] Drift checks per BNBC limits
- [ ] Torsional irregularity indicators
- [ ] P-Delta stability coefficient checks
- [ ] Serviceability summaries

### 7.4 Modal Analysis
- [/] Modal analysis module (modal.py — 3.7KB)
- [/] Modal response module (modal_response.py — 3.6KB)
- [ ] Mass modelling
- [ ] Eigen extraction via OpenSeesPy
- [ ] Mode-shape storage
- [ ] Participation ratios (>=90% check)
- [ ] Diagnostics for insufficient modes

### 7.5 Response Spectrum Analysis
- [/] RSA modules exist (response_spectrum.py in core and engineering)
- [ ] BNBC design spectrum input
- [ ] Modal combination (SRSS/CQC)
- [ ] Scaling to minimum base shear
- [ ] Code-required checks
- [ ] Benchmark and limitations document

> Note: Time-history, nonlinear, and automatic hinge workflows are explicitly excluded from V1.

---

## Phase 8 — Member-Family Expansion & Design Loops

### 8.1 One-Way Slab Design
- [/] Module exists (slab_oneway.py — 1.9KB prototype)
- [ ] Full flexural design with code references
- [ ] Shear check (Vc >= Vu)
- [ ] Min temperature & shrinkage steel
- [ ] Deflection check (L/d or direct)
- [ ] Validation fixtures

### 8.2 Two-Way Slab Design
- [/] Module exists (slab_twoway.py — 1.5KB prototype)
- [ ] Column/middle strip division
- [ ] Moment distribution per ACI Table 8.10.5
- [ ] Punching shear at columns
- [ ] Validation fixtures

### 8.3 Isolated Footing Design
- [/] Module exists (footing_isolated.py — 3KB prototype)
- [ ] Bearing/punching checks
- [ ] Geotechnical input boundaries
- [ ] Validation fixtures

### 8.4 Combined Footing Design
- [/] Module exists (footing_combined.py — 1.5KB prototype)
- [ ] Full design with validation

### 8.5 Shear Wall Design
- [/] Module exists (shear_wall.py — 2.8KB prototype)
- [ ] Combined axial + bending + shear
- [ ] Boundary element check
- [ ] Validation fixtures

### 8.6 Retaining Wall Design
- [/] Module exists (retaining_wall.py — 1.4KB prototype)
- [ ] Overturning/sliding/bearing checks
- [ ] Validation fixtures

### 8.7 Beamless Slab (Flat Plate/Flat Slab)
- [/] Module exists (slab_beamless.py — 2.7KB prototype)
- [ ] Full implementation with punching shear

### 8.8 Other Member Types (Out of V1 Core)
- [/] Staircase (staircase.py — 1.5KB prototype)
- [/] Dome (dome.py — 1.5KB prototype)
- [/] Raft (footing_raft.py — 1KB prototype)
- [/] Pile (pile.py — 3.2KB prototype)
- [/] Liquid tank (liquid_tank.py — 2.1KB prototype)
- [/] CFS (cfs.py — 1.5KB prototype)
- [ ] All require full implementation, code references, and validation before release

### 8.9 Quantity-Aware Detailing Data
- [ ] Reinforcement data linked to member design outputs
- [ ] Detailing data for each released family

### 8.10 Auto-Design Loop
- [/] Loop module (loop.py — 7KB prototype)
- [ ] User controls: allowed variables, locked values
- [ ] Iteration history storage (demand, assumptions, checks, governing failure)
- [ ] Convergence measure
- [ ] Bounded iteration count/time
- [ ] Terminal states: pass, manual-review-required, infeasible, solver-failed
- [ ] No automatic resizing crosses geometric/architectural/code/user constraints
- [ ] Reviewer can reproduce complete loop from run snapshot

---

## Phase 9 — Detailing, QTO, Costing & Report Artifacts

### 9.1 Detailing Domain Data
- [/] Rebar detailing module (detailing.py)
- [ ] Canonical reinforcement data model
- [ ] Bar-mark and schedule data
- [ ] Cover, splice/development data
- [ ] Section/elevation data
- [ ] Drawing-note data

### 9.2 SVG Detail Diagrams
- [ ] Render SVG diagrams from canonical data
- [ ] Beam elevation with bar locations, cutoffs, stirrup zones
- [ ] Column cross-section with bar layout, tie arrangement
- [ ] Slab plan with bar arrangement
- [ ] Visual regression tests for SVG output
- [ ] Release status label on every diagram

### 9.3 Quantity Take-Off
- [/] QTO module (qto.py — 1.8KB prototype)
- [ ] Derive quantities from exact model/design snapshot
- [ ] Concrete volume (m3) per member type
- [ ] Reinforcement weight (kg) per member type
- [ ] Formwork area (m2)
- [ ] Calculation basis and unit assumptions

### 9.4 PWD Rate-Based Costing
- [ ] Versioned PWD-rate datasets (separate from quantities)
- [ ] Rate source and effective date display
- [ ] Pricing exclusions stated
- [ ] Cost per element and overall total

### 9.5 PDF Report Generation
- [/] Report utilities exist (reporting.py, core/reports/ dir)
- [ ] Templated PDF with cover page
- [ ] Scope/disclaimer section
- [ ] Revision and approval state
- [ ] Source references and code-data release
- [ ] Input summary, load combinations, analysis results
- [ ] Design results with governing cases
- [ ] Warnings section
- [ ] QTO and costing sections
- [ ] Appendices
- [ ] Draft/reviewed/approved watermarks
- [ ] Limitation statement

### 9.6 Artifact Integrity
- [ ] Artifact checksum computation
- [ ] Deterministic naming scheme
- [ ] Storage access controls
- [ ] Report reproduction tests (same snapshot = same checksum)

---

## Phase 10 — Production Readiness & Controlled Rollout

### 10.1 Authentication & Authorization
- [ ] User authentication (JWT/SSO)
- [ ] Organisation/project authorization model
- [ ] Reviewer permissions and role enforcement
- [ ] Audit logging for security events
- [ ] Password/SSO policy
- [ ] Service-account rules

### 10.2 Safe Uploads
- [ ] File type/size validation
- [ ] Quarantine / malware scanning strategy
- [ ] Object storage for uploaded files
- [ ] Document retention/deletion policy
- [ ] No execution of user-provided scripts

### 10.3 Deployment
- [/] Docker setup exists (Dockerfile, docker-compose.yml, nginx/)
- [ ] Frontend production image build
- [ ] API/worker production images
- [ ] Migration job in deployment pipeline
- [ ] Reverse proxy / TLS configuration
- [ ] Secure headers, CORS production config
- [ ] Health/readiness/liveness checks (partially done)
- [ ] Structured logging
- [ ] Metrics collection
- [ ] Distributed tracing
- [ ] Alert configuration

### 10.4 Operational Safety
- [ ] Backup/restore procedures
- [ ] Disaster-recovery test
- [ ] Migration rollback strategy
- [ ] Dependency/SBOM/license scanning
- [ ] Secret rotation procedure
- [ ] Incident runbooks

### 10.5 Controlled Rollout
- [ ] Feature flags system
- [ ] Pilot cohort selection
- [ ] Engineering review feedback collection
- [ ] Staging E2E test suite pass
- [ ] Security review pass
- [ ] Recovery drill pass
- [ ] Performance test pass
- [ ] Accessibility review pass
- [ ] Operational-readiness review
- [ ] Release evidence and known limitations signed off

---

## Cross-Cutting Concerns (All Phases)

### Workbook Inventory & Parity Program
- [ ] Machine-readable inventory of all 34 Excel workbooks
- [ ] For each: hash, sheets, purpose, standard edition, author assumptions
- [ ] Input cell identification (yellow/highlighted)
- [ ] Formula extraction and documentation
- [ ] Classification: reliable reference / legacy / incomplete / out of V1 scope
- [ ] Approved fixtures per workbook
- [ ] Corresponding Python module and test identifiers

### Engineering Validation Board
- [ ] Capability matrix for each calculation
- [ ] Requirements per calculation
- [ ] Code citations per calculation
- [ ] Numerical method documentation
- [ ] Hand-calc / workbook comparison
- [ ] Boundary/error handling documentation
- [ ] Test coverage per feature
- [ ] UI/report language review
- [ ] Reviewer approval tracking

### Reference Data Governance
- [ ] Confirm exact code editions, clauses, and source files that may be encoded
- [ ] Define V1 building typology / member families / max dimensions / storeys
- [ ] Identify accountable engineering validator
- [ ] Define benchmark sources and tolerances per calculation type
- [ ] Define user/org/auth model for pilot
- [ ] Define data hosting, retention, backup, restore strategy
- [ ] Determine if cost estimation + report export are in first pilot
- [ ] Define regional/legal disclaimers and report-signing process

---

## Immediate Next Steps (Recommended Priority)

1. **Install & validate dependencies** — Fix requirements.txt install, fix frontend package-lock.json, verify both build
2. **Bootstrap Alembic** — Create initial migration, test migrate-forward from empty
3. **Complete the codes registry + combination engine** — Codex was working on this when credits ran out
4. **Wire project revision persistence** — Connect revision API routes to actual database operations
5. **Create first benchmark fixtures** — Portal frame, two-storey frame with hand-calculated expected values
6. **Refactor OpenSees adapter** — Extract solver-neutral StructuralModel from the 36KB monolith
7. **Implement child-process isolation** — Run OpenSeesPy in subprocess, not Celery worker directly
8. **Fix frontend build** — Resolve broken dependency tree, get npm install and npm run build working
9. **Replace all mock/demo data** — Remove hardcoded dashboard data, wire to real APIs
10. **Beam + column calculators** — Refactor into pure typed functions with dimensional tests
