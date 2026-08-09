# Database migrations

This directory is the Phase 1 migration boundary. Production startup must not
call `Base.metadata.create_all`; schema changes must be represented by reviewed
Alembic migrations and applied as an explicit deployment step.

Until Alembic is bootstrapped, local development may opt into
`CREATE_SCHEMA_ON_STARTUP=true` in `app/.env`. That switch is intentionally
disabled by default and must never be enabled in a shared environment.
