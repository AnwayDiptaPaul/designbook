# Runtime validation

The maintained unit suite does not prove that PostgreSQL, Redis, Celery, or
container networking are working. Use the development compose stack for that
boundary:

```text
docker compose -f app/docker-compose.yml up --build -d
python tools/runtime_smoke.py
docker compose -f app/docker-compose.yml logs --tail=100 api celery_worker
```

The smoke command checks `/api/health`, `/api/ready`, and `/api/capabilities`.
It returns a non-zero status when the API is unreachable, the database is not
ready, or the capability boundary is unexpected. The compose file enables
schema bootstrap and analysis execution only for local development. Production
must use reviewed migrations and explicitly provisioned secrets/settings.

To clean up the local stack:

```text
docker compose -f app/docker-compose.yml down -v
```