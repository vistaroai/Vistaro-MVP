# Vistaro

Agentic AI platform for small-business growth. This repository is the
`REPO-001` bootstrap: a minimal FastAPI service, a minimal React web app, local
services, and CI. It does not contain product features, authentication,
database migrations, or Sentinel approvals yet.

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

### 2. Web

In a second terminal:

```bash
cd apps/web
pnpm install --frozen-lockfile
pnpm dev
```

Open <http://localhost:5173>.

The API does not need Postgres or Redis to start; database-backed features
arrive in `DB-001`. Start local services when you need them:

```bash
docker compose -f infra/docker-compose.yml up -d
```

## Checks

```bash
cd apps/api
uv run ruff check .
uv run mypy src
uv run lint-imports
uv run pytest -q

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
apps/api/                  FastAPI service
apps/web/                  React + TypeScript + Vite app
infra/docker-compose.yml   local Postgres, Redis, Mailpit
.github/workflows/ci.yml   lint, types, tests, import rules, secret scan
```

## Environment variables

Copy `.env.example` to `.env`; it lists names only. Never commit `.env`, keys,
tokens, or customer data. CI runs a secret scan.

## Status

Bootstrap complete. `REPO-001` was merged through PR #1 on 2026-10-23, and CI
passed on that PR. Docker Compose is still not verified because Docker is not
installed locally. See `docs/PROJECT_ROADMAP.md` for the real task status and
`docs/ACTIVE_TASKS.md` for the current queue.
