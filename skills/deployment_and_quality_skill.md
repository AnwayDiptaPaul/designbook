# Deployment & Quality Hardening Skill

When building the CI/CD pipelines, modifying Dockerfiles, or creating environment orchestration scripts, strictly uphold these stability operations.

## Idempotent Bash Orchestration
Scripts initializing the runtime must act smoothly independent of past execution footprints. 
- **`dev.sh`**: Ensure traps capture Unix signals efficiently (like `SIGINT` or `Ctrl+C`). It must explicitly clean up and terminate deeply nested backend workers (Uvicorn zombies capturing port `8000`) and frontend node servers (Vite zombies holding port `5173`) before exiting.
- **`setup_db.sh`**: Implement rigorous PostgreSQL bootstrapping. The script MUST contain native `IF NOT EXISTS` assertions allowing it to execute safely regardless of whether databases, tables, or roles were provisioned in preceding sessions.

## Offline Functional Resilience
DesignBook acts as local standalone "Engineering Client". It cannot fail simply due to network isolations.
- Ensure all packages and binaries map securely to the native `.venv`.
- Disallow inclusion of any standard HTML CDN links indicating dynamic fetches for component parts. 

## Dependency Hygiene & Audits
- Python dependencies (`requirements.txt`) should maintain minimum-version constraints (`>=`) known to interoperate optimally with the provided `OpenSeesPy` Linux bindings. Strict pinning is optional but ranges must never be unbounded.
- No `package.json` configurations are allowed to propagate critical `npm audit` violations.
- Avoid introducing unverified 3rd party UI libraries. If a UI effect is needed, build it utilizing `lucide-react` or Tailwind CSS logic.

## Security Parameters
- The backend API must actively reject cross-site origin access that hasn't been listed explicitly (Vite `localhost` / Prod mappings).
- The `.env` template handling must be rigorously protected. Ensure all SQL connection string parameters are fetched purely through Pydantic BaseSettings mapped specifically against secure system paths.
