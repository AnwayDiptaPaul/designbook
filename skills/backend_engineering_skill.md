# Backend Engineering & Python Architecture Skill

When executing logic, building APIs, or fixing bugs within the python backend (`app/backend/`), this architectural mindset is mandatory.

## Frameworks & Typings Core
- **Primary Framework**: FastAPI with asynchronous path operations (`async def`). 
- **Type Checking (Mission Critical)**: The backend adheres to extremely rigid static typing enforced by **Pyre**. Any Python modifications must maintain `exit code 0` upon Pyre validation within the `.venv`. Do not suppress type warnings using ignore flags unless explicitly documented and theoretically unavoidable.
- **Data Schemas**: Strict **Pydantic** typing acts as the absolute border between the frontend HTTP requests, the API, and internal services (`schemas/` directory conventions). Boundary schemas must reject structurally invalid geometry natively (e.g. `Field(..., gt=0)`).

## Heavy Computing Isolation (OpenSeesPy)
- OpenSeesPy acts as the numerical workhorse and relies on inherently stateful C++ underlying instances.
- **CRITICAL**: The `StructuralDesignService` and `OpenSeesModelBuilder` must NEVER retain dirty state between API calls. To prevent shared state collisions (like `IndexError` across repeated consecutive runs) and fatal C++ engine segfaults crashing the API worker:
  - All stress-test loops and heavy solver functions MUST be evaluated within isolated multiprocessing containers.
  - Call `ops.wipe()` meticulously natively when a computation ends or errors out.

## Database & Persistence
- **SQLAlchemy 2.0+ ORM** with asynchronous engines (`asyncpg`).
- Object interaction should be structured carefully through Sessions passed natively via FastAPI Dependencies.
- Never write raw SQL. Never hardcode PostgreSQL URIs (always read configuration from `.env`).

## Standard Coding Practices
- Exclusively use relative module imports referencing `backend.` safely, avoiding absolute paths relying on `sys.path` injection. **Exception**: Standalone validation scripts (`complete_design_problems.py`, `edge_case_validation.py`) that run outside the FastAPI process may use `sys.path.insert` at the top to bootstrap the import root.
- Implement descriptive docstrings for all physical engineering routines, explicitly naming the equations, constraints, and standard reference points utilized.
