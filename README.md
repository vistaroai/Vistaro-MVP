# Vistaro

Agentic AI platform for small-business growth. This repository is the `REPO-001`
bootstrap plus the `DB-001` base schema: a minimal FastAPI service, a minimal
React web app, local services, CI, and Alembic migrations for the identity and
tenancy tables. It does not contain product features, authentication, or
Sentinel approvals yet.

## Prerequisites

- Python 3.12 (the project pins `3.12`; `uv` can install it)
- [uv](https://docs.astral.sh/uv/)
- Node.js 22 or newer
- pnpm 12
- Docker Desktop (optional; needed for Postgres, Redis, and Mailpit)

Verified locally with Python 3.12.15, Node.js 24.22.1, pnpm 12.15.0, and
uv 0.13.5.

## Quick start (fresh clone)

```bash
git clone https://github.com/vistaroai/Vistaro-MVP.git
cd Vistaro-MVP
cp .env.example .env
```

On Windows PowerShell, use `Copy-Item .env.example .env` instead of `cp`. If
PowerShell blocks `pnpm` because of the script execution policy, use
`pnpm.cmd` or run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal.

### 1. API

```bash
cd apps/api
uv sync
uv run uvicorn vistaro.main:app --reload --port 8000
```

Check it:

```bash
curl http://127.0.0.1:8000/healthz
```

Expected: `{"status":"ok","environment":"local"}`. On PowerShell, use
`Invoke-RestMethod http://127.0.0.1:8000/healthz` instead of `curl`.

### 3. Web

In a second terminal:

```bash
cd apps/web
pnpm install --frozen-lockfile
pnpm dev
```

Open <http://localhost:5173>.

The API health check does not need Postgres or Redis to start. Other API routes
use Redis-backed rate limiting and return `503` while Redis is unavailable; run
the local services before exercising those routes.

### 2. Database (roles, schema, migrations)

Start the local services. The compose file also mounts `infra/initdb/`, which
creates the roles (`vistaro_migrator` owns the schema; `vistaro_app` has no
`BYPASSRLS`) and the `citext` extension on a fresh Postgres volume:

```bash
docker compose -f infra/docker-compose.yml up -d
```

If your `vistaro` Postgres volume was created before `infra/initdb/` was
mounted, run the same script once; it is idempotent:

```bash
docker exec -i vistaro-postgres-1 psql -U vistaro -d vistaro < infra/initdb/01_roles_and_extensions.sql
```

(On PowerShell: `Get-Content infra/initdb/01_roles_and_extensions.sql -Raw |
docker exec -i vistaro-postgres-1 psql -U vistaro -d vistaro`.)

Wait for Postgres to be healthy, then run the migrations:

```bash
cd apps/api
uv run alembic upgrade head
```

Migrations run as `vistaro_migrator` (via `MIGRATOR_DATABASE_URL` in `.env`).
`DATABASE_URL` is the application connection; it uses `vistaro_app`, which
cannot bypass Row Level Security.

## Checks

```bash
cd apps/api
uv run ruff check .
uv run mypy src
uv run lint-imports
uv run pytest -q
```

The tenancy tests (`tests/test_tenancy.py`) need the local Postgres service
running (they exercise the real database); without it they skip with a
note. CI runs a Postgres service so they never skip there.

Frontend checks:

```bash
cd ../web
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## Project structure

```text
CLAUDE.md, AGENTS.md       rules and agent pointer
STARTUP_*.md               product and business context
docs/                      architecture, roadmap, tasks, warnings, playbook, ADRs
apps/api/                  FastAPI service, Alembic migrations
apps/web/                  React + TypeScript + Vite app
infra/docker-compose.yml   local Postgres, Redis, Mailpit
infra/initdb/              one-time role/extension bootstrap for Postgres
.github/workflows/ci.yml   lint, types, tests, import rules, secret scan
```

## Environment variables

Copy `.env.example` to `.env`; it lists names only. Never commit `.env`, keys,
tokens, or customer data. CI scans for secrets and audits locked Python and
production JavaScript dependencies. Dependabot checks Python, pnpm, and GitHub
Actions dependencies weekly.

Browser requests that change state must first obtain a CSRF token from `GET
/csrf`, keep the response token in memory, and send it in `X-CSRF-Token`. The
request must come from the configured `WEB_ORIGIN`. This endpoint issues only a
CSRF token; authentication and session issuance are not implemented.

## Status

`DB-001` base schema is implemented and verified locally. Docker Desktop is
installed, the Postgres service runs via Docker Compose, and the Alembic
migrations have been verified on empty and seeded databases. See
`docs/PROJECT_ROADMAP.md` for the real task status and `docs/ACTIVE_TASKS.md`
for the current queue.
