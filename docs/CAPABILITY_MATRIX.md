# DesignBook capability matrix

This matrix is intentionally conservative. “Prototype” means code exists but
has not met the calculation, provenance, and reviewer gates in the
implementation plan. It must not be shown to end users as an approved result.

| Capability | Current state | Release gate |
|---|---|---|
| Project CRUD | Implemented prototype | Revisioned snapshots, authorization, migrations, contract tests |
| Geometry/grid input | Implemented prototype | Topology validator, canonical model, persisted revisions |
| Gravity loads/combinations | Implemented prototype | Unit tests, code registry, benchmark fixtures |
| Linear frame analysis | Implemented prototype | Isolated worker, deterministic results, reviewed benchmarks, code-scope approval |
| Beam/column design | Implemented prototype | Pure typed calculations, workbook/hand parity, reviewer approval |
| Slab/foundation/wall design | Prototype modules present | One-family-at-a-time validation and released scope |
| Wind/seismic ESFM | Prototype modules present | BNBC source registry, lateral benchmarks, governing-case output |
| Response spectrum/P-Delta | Prototype modules present | Mass/modal validation and release-specific acceptance tests |
| Time history/pushover | Stub/planned | Separate advanced-analysis release |
| Excel integration | Stub/partial | Workbook inventory, parity fixtures, safe import/export boundary |
| Analysis job progress | Opt-in prototype | Database-backed state transitions, queue events, retry/cancel semantics, worker smoke tests |
| Frontend workflow | Demo/prototype | Server-backed forms, no mock data, E2E and accessibility tests |
| Detailing/QTO/reporting | Prototype | Snapshot-bound artifacts, visual QA, report traceability |
| Authentication/approval | Planned | Roles, project authorization, audit trail, reviewer workflow |

The status must be updated alongside every release and linked to benchmark
evidence rather than to a code-coverage percentage.
