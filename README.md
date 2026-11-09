# RaceOps

RaceOps is a research-driven web platform for small karting and grassroots
motorsport teams. It preserves the context and reasoning around a session:
what happened, what was observed, what changed and what happened afterwards.

RaceOps complements tools such as AiM RaceStudio, MyChron and MoTeC. It is
not a telemetry acquisition or professional analysis replacement.

## Current status

Phase 6 — Identity and authorization, completed and approved. Phase 7 —
Operational Base, completed, approved and published as `v0.2.0`. Phase 8 has
started: its contract is approved and Session persistence is implemented and
awaiting block approval. No Session endpoints exist yet. RaceOps exposes
operational APIs for Drivers, Vehicles, Tracks and Events
with database-enforced Team isolation, in addition to teams, users and
team-scoped memberships; hashes
passwords with Argon2id; issues short-lived membership-scoped JWTs; re-resolves
identity and role state from PostgreSQL; and provides an atomic local
administrator bootstrap. Login and `/auth/me` are available. Deny-by-default
RBAC, Team scope and Visibility policies are ready for the operational
resources that begin in Phase 7. Production configuration rejects known
development credentials, placeholder or short JWT secrets, and CORS permits
only explicitly configured origins.

## Technology

- Python 3.12+
- FastAPI
- SQLAlchemy 2.x and Psycopg 3
- PostgreSQL
- Alembic
- pwdlib with Argon2 and PyJWT
- pytest, HTTPX, Ruff and mypy
- Docker and Docker Compose

## Local prerequisites

- Python 3.12 or newer supported version
- Git
- Docker with Docker Compose

The machine currently used for development has Python 3.12.4.

## Run the complete stack with Docker

Build the API image, start PostgreSQL, apply migrations and wait for the API
health check:

```powershell
docker compose up -d --build --wait
docker compose ps -a
```

Compose runs three services:

- `db`: PostgreSQL with a persistent named volume;
- `migrate`: applies `alembic upgrade head` and then exits;
- `api`: starts only after the database is healthy and migrations succeed.

`migrate` showing `Exited (0)` is expected: the one-time job completed
successfully. `db` and `api` should show `healthy`.

The API is available at `http://127.0.0.1:8000`. PostgreSQL is exposed only on
the local machine at `127.0.0.1:55432`.

Useful commands:

```powershell
docker compose logs -f api
docker compose ps -a
docker compose stop
docker compose up -d --wait
```

`docker compose stop` preserves containers and database data. Do not run
`docker compose down --volumes` unless you intentionally want to delete the
local RaceOps database.

## Run the API directly for development

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
docker compose up -d --wait db
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn raceops.main:app --reload
```

Then open `http://127.0.0.1:8000/health` or the generated API documentation
at `http://127.0.0.1:8000/docs`.

Available system endpoints:

- `/health`: returns `200` when the API process is alive;
- `/ready`: returns `200` when PostgreSQL answers `SELECT 1`, otherwise
  returns `503` without exposing connection details.

With the database container healthy and migrations applied, `/ready` returns
`200`. If PostgreSQL is stopped or cannot be reached, it returns `503` while
`/health` continues to report whether the API process itself is alive.

The development database is exposed on `localhost:55432` so RaceOps does not
collide with a PostgreSQL installation already using the standard host port
`5432`. PostgreSQL continues to use `5432` inside its container.

To stop only the database without deleting its persisted data:

```powershell
docker compose stop db
```

Running `docker compose up -d --wait db` later reuses the same named volume.
Do not run `docker compose down --volumes` unless you intentionally want to
delete the local RaceOps database.

## Configuration

RaceOps reads variables prefixed with `RACEOPS_`. To customize local values:

```powershell
Copy-Item .env.example .env
```

`.env` is ignored by Git. Known development database credentials, the example
JWT secret and JWT secrets shorter than 32 characters are rejected
automatically when `RACEOPS_ENV=production`.

## Bootstrap the first administrator

Apply migrations first, then run the local bootstrap command. The password is
requested twice through hidden terminal input and is never accepted as a
command-line argument:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m raceops.iam.bootstrap_admin `
  --email admin@example.com `
  --team-name "Example Racing Team"
```

Team, User and Administrator Membership are committed in one transaction. A
conflict rolls back all three records. This command is intended for the first
controlled local setup; it is not public registration.

## Authenticate and inspect the active identity

With the API running, authenticate the bootstrapped administrator:

```powershell
$loginBody = @{
  email = "admin@example.com"
  password = "your-administrator-password"
} | ConvertTo-Json

$login = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/auth/login" `
  -ContentType "application/json" `
  -Body $loginBody

Invoke-RestMethod `
  -Method Get `
  -Uri "http://127.0.0.1:8000/api/v1/auth/me" `
  -Headers @{ Authorization = "Bearer $($login.access_token)" }
```

The same flow is available interactively at `http://127.0.0.1:8000/docs`.
When a user belongs to multiple active teams, login returns
`team_context_required`; repeat the request with one returned `team_id`.

## Manage Drivers

With a valid membership token, the Driver API is available at:

- `POST /api/v1/drivers`;
- `GET /api/v1/drivers` with `status`, `limit` and `offset` filters;
- `GET /api/v1/drivers/{driver_id}`;
- `PATCH /api/v1/drivers/{driver_id}`;
- `POST /api/v1/drivers/{driver_id}/activate`;
- `POST /api/v1/drivers/{driver_id}/deactivate`.

Administrator and Team Manager can manage Drivers. Engineer and Mechanic can
read same-Team Drivers. A Driver can only read the profile linked to the
current User. Ownership always comes from the token; `team_id` is rejected in
request bodies. There is intentionally no DELETE endpoint.

## Manage Vehicles

With a valid membership token, the Vehicle API is available at:

- `POST /api/v1/vehicles`;
- `GET /api/v1/vehicles` with `status`, `limit` and `offset` filters;
- `GET /api/v1/vehicles/{vehicle_id}`;
- `PATCH /api/v1/vehicles/{vehicle_id}`;
- `POST /api/v1/vehicles/{vehicle_id}/mark-ready`;
- `POST /api/v1/vehicles/{vehicle_id}/mark-maintenance`;
- `POST /api/v1/vehicles/{vehicle_id}/mark-unavailable`;
- `POST /api/v1/vehicles/{vehicle_id}/retire`.

Administrator and Team Manager can manage Vehicles. Engineer and Mechanic can
read same-Team Vehicles. Driver access remains denied until Phase 8 can prove
a Session relationship. A Vehicle starts `READY`, `RETIRED` is terminal and
only `READY` will be assignable. Ownership comes from the token and status
changes use explicit commands; there is no DELETE endpoint.

## Manage Tracks and Events

The Track catalog is available at `POST/GET /api/v1/tracks` and
`GET/PATCH /api/v1/tracks/{track_id}`. Every role can read same-Team Tracks;
Administrator, Team Manager and Engineer can create and update them.

Events are available at `POST/GET /api/v1/events`,
`GET/PATCH /api/v1/events/{event_id}` and the explicit commands `activate`,
`complete` and `cancel`. Administrator, Team Manager and Engineer manage
Events; Mechanic has read access. Driver Event access remains deferred until
Session can prove a relationship. Every Event references a same-Team Track,
starts `PLANNED`, preserves valid dates and has no DELETE endpoint.

## Errors and request correlation

Every HTTP response includes `X-Request-ID`. A valid UUID supplied in that
header is preserved; any missing or invalid value is replaced. Error responses
use `application/problem+json` and return the same value as `trace_id`:

```json
{
  "type": "https://raceops.local/problems/resource-not-found",
  "title": "Resource not found",
  "status": 404,
  "detail": "The requested resource was not found.",
  "instance": "/api/v1/example",
  "code": "RESOURCE_NOT_FOUND",
  "trace_id": "8e729efa-7124-4498-8f71-ddf6b329f9fc"
}
```

RaceOps application logs are JSON objects written to standard output. They use
route templates instead of concrete URLs and never serialize request bodies,
authorization headers, cookies, connection strings or arbitrary log fields.
Unexpected exceptions expose only a generic response; server logs retain the
exception type and safe stack locations without the exception message.

## Verify

```powershell
.\.venv\Scripts\python.exe -m ruff format --check src tests migrations
.\.venv\Scripts\python.exe -m ruff check src tests migrations
.\.venv\Scripts\python.exe -m mypy src tests
.\.venv\Scripts\python.exe -m pytest
```

The database migration round-trip is opt-in because it requires the local
PostgreSQL container:

```powershell
$env:RACEOPS_RUN_DB_TESTS = "1"
.\.venv\Scripts\python.exe -m pytest tests\integration\test_migrations.py
Remove-Item Env:RACEOPS_RUN_DB_TESTS
```

## Continuous integration

The workflow in `.github/workflows/ci.yml` runs on pushes to `main`, pull
requests and manual dispatch. It has read-only repository permissions and two
independent jobs:

1. **Python quality and tests:** starts PostgreSQL 18.6, checks Ruff formatting
   and lint, runs mypy, executes all tests with at least 90% coverage and uses
   `alembic check` to detect model changes without a migration.
2. **Container smoke test:** validates Compose, builds the runtime image,
   starts the complete stack, checks the HTTP endpoints and verifies the
   non-root runtime constraints.

The Docker stack created by CI is ephemeral and its volume is removed only on
the disposable GitHub runner. The workflow does not delete the local database.

The first complete CI validation passed in
[run 42399043070](https://github.com/oraclesupreme63-droid/RACEOPS/actions/runs/42399043070),
including both the Python quality job and the container smoke test.

## Documentation

- [Project roadmap](docs/roadmap.md)
- [Architecture package](docs/architecture/README.md)
- [Architecture decisions](docs/decisions/README.md)
- [Development runbook](docs/development/runbook.md)
- [Gate G5 assessment](docs/development/gate-g5-assessment.md)
- [Current project status report](docs/development/project-status-report-2026-11-09.md)
- [Phase 6 checklist](docs/development/phase-6-checklist.md)
- [Phase 6 Block 6.2 report](docs/development/phase-6-block-6.2-report-2026-11-08.md)
- [Phase 6 Block 6.3 report](docs/development/phase-6-block-6.3-report-2026-11-08.md)
- [Phase 6 Block 6.4 report](docs/development/phase-6-block-6.4-report-2026-11-08.md)
- [Phase 6 Block 6.5 report](docs/development/phase-6-block-6.5-report-2026-11-08.md)
- [Phase 6 closure report](docs/development/phase-6-block-6.6-report-2026-11-08.md)
- [Phase 7 checklist](docs/development/phase-7-checklist.md)
- [Phase 7 operational contract](docs/operations/operational-base-contract.md)
- [Phase 7 Block 7.1 report](docs/development/phase-7-block-7.1-report-2026-11-08.md)
- [Phase 7 Block 7.2 report](docs/development/phase-7-block-7.2-report-2026-11-08.md)
- [Phase 7 Block 7.3 report](docs/development/phase-7-block-7.3-report-2026-11-08.md)
- [Phase 7 Block 7.4 report](docs/development/phase-7-block-7.4-report-2026-11-08.md)
- [Phase 7 Block 7.5 report](docs/development/phase-7-block-7.5-report-2026-11-09.md)
- [Phase 7 closure report](docs/development/phase-7-block-7.6-report-2026-11-09.md)
- [Phase 7 implementation traceability](docs/development/phase-7-traceability.md)
- [Phase 8 checklist](docs/development/phase-8-checklist.md)
- [Phase 8 Block 8.1 report](docs/development/phase-8-block-8.1-report-2026-11-09.md)
- [Phase 8 Block 8.2 report](docs/development/phase-8-block-8.2-report-2026-11-09.md)
- [Session Learning Loop contract](docs/sessions/session-learning-loop-contract.md)
- [Identity and authorization contract](docs/identity/identity-contract.md)
- [Technical learning roadmap](docs/development/learning-roadmap.md)
- [Domain package](docs/domain/README.md)
- [Requirements package](docs/requirements/README.md)
- [Research](docs/research/research-plan.md)

## Scope discipline

RaceOps remains a modular monolith. Phase 7 built the minimum operational
resources required by Session. Phase 8 now implements the Session Learning
Loop in vertical, independently approved blocks.

