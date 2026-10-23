# DEVELOPMENT GUIDE — Vistaro

Version 1.0 · 2026-10-18 · The practical "how to build it" companion to `/docs/ARCHITECTURE.md`.
Rules: `/CLAUDE.md`. Task list: `/docs/PROJECT_ROADMAP.md`. Queue: `/docs/ACTIVE_TASKS.md`. Per-task instructions and prompts: `/docs/TASK_PLAYBOOK.md` (this guide holds the patterns and conventions those instructions rely on).

## 0. How to use this guide

- **Everything here is a plan, not verified code.** No repository existed when this was written. Commands are the *target* commands for the chosen stack. After you create the repo, run each one and record the result in `CLAUDE.md` §12 ("Verified commands"). Until then treat them as unverified.
- **Code sketches are illustrative patterns**, not drop-in code. They show the shape of the solution so you can write and validate your own version. (Founder preference: you validate your own code; AI agents should explain patterns and propose small diffs rather than rewrite large areas.)
- Versions are not pinned here. Pin exact versions in lockfiles when you install, and prefer releases at least two weeks old.
- Items marked **Verify** depend on outside providers whose offerings change.

---

## 1. Accounts and prerequisites checklist

| Need | Why | When |
|---|---|---|
| GitHub account and repository (private) | Source control, CI | Day 1 |
| GitHub Student Developer Pack (if eligible) | Possible cloud and tool credits. **Verify** current offers | Day 1 |
| Python 3.12 and `uv` | Backend | Day 1 |
| Node.js (current LTS) and `pnpm` | Frontend | Day 1 |
| Docker Desktop | Local Postgres and Redis | Day 1 |
| LLM provider API key (default Anthropic) | Agents. Use a separate key per environment, with a spending limit set in the provider console | Before `AI-002` |
| Sentry account (free tier) | Error tracking | Before staging |
| Cloudflare account | Pages and R2 | Before staging |
| Render account | API, worker, Postgres, Redis. **Verify** plan, region, `pgvector` support | Before staging |
| Resend account and a domain | Email. Requires DNS (SPF, DKIM) | Before `AUTH-001` email verification |
| Meta developer account and app | Instagram and Facebook publishing. Development mode first. **Verify** requirements | Before `INT-002` |
| Domain name for Vistaro | App URL and email | After `NAME-001` |

---

## 2. Repository bootstrap (`REPO-001`)

Target commands (unverified until run):

```bash
# 1. Create repo layout
mkdir vistaro && cd vistaro && git init
mkdir -p apps/api apps/web infra docs/adr .github/workflows
# 2. Copy in: CLAUDE.md, AGENTS.md, docs/*.md, STARTUP_*.md

# 3. Backend
cd apps/api
uv init --package --name vistaro            # or create pyproject.toml manually
uv add fastapi "uvicorn[standard]" "sqlalchemy>=2" alembic psycopg[binary] pydantic-settings \
       celery redis structlog sentry-sdk argon2-cffi authlib httpx cryptography
uv add --dev pytest pytest-asyncio pytest-cov ruff mypy import-linter factory-boy

# 4. Frontend
cd ../web
pnpm create vite . --template react-ts
pnpm add @tanstack/react-query react-router-dom zod react-hook-form openapi-fetch
pnpm add -D tailwindcss vitest @testing-library/react playwright openapi-typescript eslint prettier
```

Add at the repo root: `.gitignore` (include `.env`, `*.pem`, `node_modules`, `.venv`), `.editorconfig`, `.env.example` (names only), `README.md` with the verified commands, `infra/docker-compose.yml` (Postgres, Redis, optional Mailpit for local email).

**Acceptance for `REPO-001`:** a fresh clone installs and runs both apps using only the README; CI runs on a pull request; no secrets in history.

---

## 3. Local development

### 3.1 Services (docker-compose)

| Service | Purpose |
|---|---|
| `postgres` | Primary database. Enable `citext`; add `pgvector` only when Phase 3 starts |
| `redis` | Celery broker, rate limits |
| `mailpit` | Catch local emails |

### 3.2 Environment variables (names only; values never committed)

| Name | Purpose |
|---|---|
| `DATABASE_URL` | App connection (role `vistaro_app`) |
| `MIGRATOR_DATABASE_URL` | Migration connection (role `vistaro_migrator`) |
| `REDIS_URL` | Broker and limits |
| `SESSION_SECRET` | Signing and CSRF |
| `ENCRYPTION_KEYS` | Key ID to key map for connection tokens |
| `LLM_PROVIDER`, `LLM_API_KEY` | LLM access |
| `LLM_MODEL_LARGE`, `LLM_MODEL_SMALL` | Tier to model mapping (set at `DEC-002`) |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Google sign-in |
| `META_APP_ID`, `META_APP_SECRET` | Meta Graph API |
| `RESEND_API_KEY` | Email |
| `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET` | File storage |
| `SENTRY_DSN` | Error tracking |
| `APP_ENV` | `local`, `staging`, `production` |
| `WEB_ORIGIN` | CORS and cookie settings |

### 3.3 Run (target)

```bash
docker compose -f infra/docker-compose.yml up -d
cd apps/api && uv run alembic upgrade head
uv run uvicorn vistaro.main:app --reload            # API
uv run celery -A vistaro.worker worker -l info      # worker
uv run celery -A vistaro.worker beat -l info        # scheduler
cd ../web && pnpm dev                                # web
```

---

## 4. Backend conventions

**Module template** (each of `auth`, `sentinel`, `agents`, `orbit`, `clarity`, `muse`, `convert`, ...):

```
module/
  models.py     SQLAlchemy models (private to the module)
  schemas.py    Pydantic request/response types (shareable)
  repo.py       All SQL for this module
  service.py    Public interface: the ONLY thing other modules import
  router.py     FastAPI routes; calls service only
  tasks.py      Celery tasks (thin; call service)
```

**Rules:**
1. Routers → services → repos. No SQL in routers or services.
2. Other modules import only `service.py` and `schemas.py` (enforced by `import-linter` contracts in `pyproject.toml`).
3. Every route declares its permission through the Sentinel dependency.
4. Errors: raise typed exceptions (`NotFound`, `PermissionDenied`, `Conflict`, `ValidationFailed`); a single handler converts them to the standard envelope.
5. Logging: `structlog` with bound `request_id`, `workspace_id`, `task_id`. Never log secrets or message bodies.
6. Time and IDs through helpers in `core` so tests can control them.
7. Typing: mypy strict on `core`, `sentinel`, `auth`; progressively strict elsewhere.

### 4.1 Pattern: tenant-scoped transaction (illustrative)

```python
# core/db.py  (sketch, adapt and verify)
from contextlib import contextmanager
from sqlalchemy import text

@contextmanager
def tenant_session(session_factory, workspace_id: str):
    with session_factory() as session:
        with session.begin():
            # transaction-local setting; safe with pooled connections
            session.execute(
                text("SELECT set_config('app.workspace_id', :wid, true)"),
                {"wid": workspace_id},
            )
            yield session
```

```sql
-- migration sketch for each tenant table
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON leads
  USING (workspace_id = current_setting('app.workspace_id', true)::uuid)
  WITH CHECK (workspace_id = current_setting('app.workspace_id', true)::uuid);
```

Roles: `vistaro_migrator` owns tables; `vistaro_app` has table privileges but no ownership and no `BYPASSRLS`. For `audit_logs`, grant only `INSERT, SELECT` to `vistaro_app`.

### 4.2 Pattern: approval gate (illustrative)

```python
# sentinel/service.py  (sketch)
def request_approval(ws_id, action_type, payload: dict, requested_by: str, task_id=None) -> str:
    policy = policies.get(ws_id, action_type)          # default: requires approval
    if not policy.requires_approval:
        audit.log(ws_id, requested_by, "approval.skipped_by_policy", action_type)
        return NO_APPROVAL_NEEDED
    payload_hash = hash_canonical_json(payload)
    approval_id = repo.insert_request(ws_id, action_type, payload, payload_hash, requested_by, task_id)
    audit.log(ws_id, requested_by, "approval.requested", approval_id)
    return approval_id

def consume(ws_id, approval_id: str, payload: dict) -> None:
    # Atomic: UPDATE ... SET status='executed' WHERE id=:id AND status='approved'
    #         AND payload_hash=:hash AND expires_at > now()   -> must affect exactly 1 row
    if not repo.consume_if_approved(ws_id, approval_id, hash_canonical_json(payload)):
        raise PermissionDenied("approval missing, changed, expired, or already used")
    audit.log(ws_id, "system", "approval.executed", approval_id)
```

The publishing code path must call `consume(...)` immediately before the external call. A test asserts that publishing without a valid approval raises.

### 4.3 Pattern: idempotent agent step (illustrative)

```python
# agents/runtime.py  (sketch)
@celery_app.task(bind=True, acks_late=True, max_retries=3)
def run_step(self, task_id: str):
    with tenant_session_for_task(task_id) as s:
        task = repo.claim(s, task_id)        # status queued -> running, returns None if already claimed
        if task is None:
            return
        try:
            handler = registry.get(task.agent_action)    # whitelist
            output = handler(task.input, ctx=build_ctx(s, task))
            repo.mark_succeeded(s, task, output)
        except Transient as e:
            repo.mark_retry(s, task, str(e))
            raise self.retry(exc=e, countdown=backoff(self.request.retries))
        except Exception as e:
            repo.mark_failed(s, task, str(e))
```

Side-effecting handlers write the external ID to the DB before returning success and check for it first on retry.

### 4.4 Pattern: validated LLM output (illustrative)

```python
# llm/structured.py  (sketch)
from pydantic import BaseModel, ValidationError

def generate_structured(client, messages, model_cls: type[BaseModel], tier="large", budget=None):
    raw = client.generate(messages, schema=model_cls.model_json_schema(), tier=tier, budget=budget)
    try:
        return model_cls.model_validate_json(raw)
    except ValidationError as err:
        repair = messages + [{"role": "user", "content": f"Output invalid: {err}. Return corrected JSON only."}]
        raw2 = client.generate(repair, schema=model_cls.model_json_schema(), tier=tier, budget=budget)
        return model_cls.model_validate_json(raw2)   # second failure raises; the step then fails visibly
```

### 4.5 Migrations

Alembic, run with the migrator role. Rules: one change per migration; reversible where possible; expand-then-contract for breaking changes; test `upgrade` and `downgrade` on an empty database and on seeded data; take a backup before any production migration.

---

## 5. Frontend conventions

```
apps/web/src/
  app/           router, providers, layout shell
  routes/        route components (thin)
  features/      auth/ workspace/ brand/ goals/ content/ approvals/ leads/ (each: components, hooks, api)
  components/    shared UI (shadcn/ui based)
  lib/api/       generated client + fetch wrapper (credentials: include, CSRF header)
  lib/auth/      session hook, guards
  tests/         unit and e2e
```

Rules:
1. API types come from the OpenAPI schema (`openapi-typescript`); regenerate in CI; fail on drift.
2. Server state with TanStack Query; local UI state with React state. No global store until needed.
3. Forms: react-hook-form + zod.
4. Every screen handles loading, empty, error, and success states (CLAUDE.md §4).
5. Accessibility basics: labels, keyboard navigation, contrast; check with an automated tool and manually.
6. Do not store tokens in `localStorage`; the session cookie is HttpOnly.
7. Approval screens must show exactly what will be published or sent (the payload the hash covers).

---

## 6. Phase 1 build guide (task by task)

Do tasks in the order of the dependency chain in the roadmap. For each: read `PROJECT_WARNINGS.md`, plan briefly, implement, verify, update docs.

### REPO-001 / INFRA-001 / TEST-001 (foundation)
1. Bootstrap per section 2. Add CI: Ruff, mypy, pytest, import-linter, frontend lint, typecheck, Vitest, secret scan.
2. Create database roles and enable `citext`. Create staging on Render and Cloudflare Pages. **Verify** `pgvector` support on the chosen Postgres plan (needed in Phase 3).
3. Write the **tenancy test first**: two workspaces, insert rows for each, query as workspace A with application filters removed, assert zero rows from B.

### DB-001
Migrations for `users`, `workspaces`, `memberships`, `sessions`, with RLS on tenant tables (`memberships` and `sessions` need careful policy design: sessions are looked up before a workspace is known, so `sessions` is not RLS-scoped by workspace but is scoped by `user_id` in code; document this exception and test it).

### AUTH-001 / AUTH-002 / AUTH-003
1. Signup and login with Argon2id; email verification token flow; Google sign-in with Authlib.
2. Server-side sessions with cookie flags; CSRF; rate limits on auth endpoints.
3. Workspace creation makes the creator `owner`. Switching workspace updates the session.
4. RBAC: one role-to-permission map; `require(permission)` dependency; tests for every role on every protected route (generate a matrix test).

### API-001
Error envelope, request ID middleware, health endpoints, OpenAPI export, generated TypeScript client, pagination helper, idempotency-key helper.

### AI-001 / AI-002
1. Task runtime per 4.3; `claim` must be atomic (`UPDATE ... WHERE status='queued' RETURNING`).
2. `LLMClient` interface plus one provider implementation; budgets; `agent_runs` recording; fake provider for tests (clearly labeled mock).
3. Structured output helper per 4.4. Tests: invalid JSON, schema violation, repair success, repair failure.

### CLA-001 / CLA-002
1. Brand profile: guided interview form (tone words, audience, banned terms, required elements, 3 to 5 sample posts). Versioned; owner approval required before use by agents.
2. Scoring: deterministic checks first, then small-tier LLM rubric. Build an eval set of 30+ examples labeled by the founders (good, off-brand, borderline) and record agreement. Tune the threshold from it (`TEST-002`).

### MUS-001 / SEN-001 / MUS-002
1. Generation: inputs are the approved brand profile, goal, and channel; output is validated JSON (`caption`, `hashtags`, `alt_text`, ...). Score; rewrite up to 2 times if below threshold; then mark `scored` and queue for approval.
2. Sentinel: implement `request_approval` and `consume` per 4.2, the approvals inbox endpoints, and audit writes.
3. Publishing: `ManualPublish` connector first (produces the final post package; owner confirms; record). Then the Meta connector in development mode. The publish function calls `consume` immediately before the external call.

### ORB-001 / ORB-002
1. Planner prompt takes goal, brand summary, and the **registry of available actions** (the model may only choose from it). Validate per ARCHITECTURE §7.2.
2. Plan review screen; approving creates `tasks` rows; a dispatcher enqueues ready steps.
3. Dashboard: goal status, step list with states, pending approvals, results. Poll every few seconds.

### CON-001 / CON-002
1. Public lead form endpoint with token, rate limit, honeypot, validation; creates contact and lead and a `lead_events` row.
2. Lead list with filters; deterministic scoring v1; stage changes recorded as events.
3. Follow-up drafting is Phase 2 (`CON-003`). In Phase 1 the owner replies manually.

### E2E-001 / DEPLOY-001
1. Playwright test of the full loop with the fake LLM provider (labeled), and one manual run with the real provider.
2. Staging deploy pipeline with manual promotion; rehearse a rollback.

---

## 7. Later phases (how to approach)

| Phase | Approach |
|---|---|
| 2 | Add `conversations`/`messages`; follow-up agent with approval; Market tables and Razorpay (test mode first); Pulse metrics ingestion from the Meta connector; SSE for status; **do `RES-001` findings before building visibility** and implement `VisibilityProvider` with repeated runs and rates |
| 3 | Embeddings provider decision (`DEC-005`), pgvector, memory store with workspace scoping; support agent grounded on store data with refusal when ungrounded; planner upgrades with eval gates |
| 4 | Forecasting baseline (simple statistical model before any ML), experiments with guardrails, anomaly alerts, competitor watch (public sources only), weekly summary, booking, re-engagement, WhatsApp (after `LEGAL-001`) |
| 5 | Security review, load tests, backup restore drill, billing, runbooks, beta onboarding |

---

## 8. Testing strategy

| Layer | Tooling | What must be covered |
|---|---|---|
| Unit | pytest, Vitest | Scoring rules, plan validation, permission map, hashing, state transitions |
| Integration | pytest with real Postgres and Redis in CI services | Routes, repos, migrations, Celery tasks, connector fakes |
| Tenancy | pytest | Cross-workspace isolation for every tenant table (generated per table) |
| Security | pytest | Approval bypass attempts, role matrix, CSRF, rate limits, upload validation |
| AI evals | pytest in `tests/evals`, run on demand and before prompt or model changes | Brand scoring agreement, plan validity rate, structured output failure rate, groundedness (Phase 3) |
| E2E | Playwright | Core loop on staging |
| Failure injection | pytest | Provider timeout, connector 429, worker crash mid-step, duplicate delivery |

Mocks and fakes are allowed in tests and must be labeled. Real-provider tests are few, run manually, and capped by cost.

**Never claim a test passed without running it.**

---

## 9. CI/CD (workflow outline)

```yaml
# .github/workflows/ci.yml  (sketch; adapt and verify)
name: ci
on: [pull_request, push]
jobs:
  api:
    runs-on: ubuntu-latest
    services:
      postgres: { image: postgres:16, env: { POSTGRES_PASSWORD: test }, ports: ["5432:5432"] }
      redis:    { image: redis:7, ports: ["6379:6379"] }
    steps:
      - uses: actions/checkout@v4
      - run: pip install uv && cd apps/api && uv sync
      - run: cd apps/api && uv run ruff check . && uv run mypy src && uv run lint-imports
      - run: cd apps/api && uv run alembic upgrade head && uv run pytest -q
  web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd apps/web && pnpm install --frozen-lockfile && pnpm lint && pnpm typecheck && pnpm test
  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "add a secret-scanning step here (for example gitleaks)"
```

Deploy workflows: staging deploys on merge to `main`; production requires a manual approval step in GitHub Environments.

---

## 10. Release and operations

### 10.1 Release checklist
1. CI green on `main`; staging deployed; smoke and e2e pass.
2. Migrations reviewed; backup taken (production).
3. Warnings register checked for items touching this release.
4. Manual promotion; watch Sentry and dashboards for 30 minutes.
5. Record the release in the roadmap change log.

### 10.2 Rollback
Redeploy the previous image; migrations are backwards-compatible for one release; if a migration must be reverted, restore from the pre-release backup only with founder approval.

### 10.3 Backups
Daily Postgres backups on the host; weekly restore into a scratch database; record the result.

### 10.4 Incident runbook (short)
Detect (alert or report) → contain (disable the affected connector or pause goals using the feature flag) → assess (audit logs, `agent_runs`) → notify affected owners if their data or channels were touched → fix → add a regression test → record in warnings.

### 10.5 Secret rotation
Rotate LLM, Meta, and email keys on suspicion or schedule; rotate encryption keys by adding a new `key_id`, re-encrypting tokens in a job, then retiring the old key.

### 10.6 Cost watch
Weekly review of cost per goal and per workspace from `agent_runs`; provider-side spending limits set as a backstop.

---

## 11. SEVA 75-day mapping (only if selected; proposed)

Two builders. Anushka: frontend and platform. Dimple: AI and backend. Shared: tests and docs.

| Days | Anushka | Dimple | Both |
|---|---|---|---|
| 1–15 | `REPO-001`, app shell (`UI-001`), auth screens | DB schema (`DB-001`), auth backend (`AUTH-001`) | Interviews (`VAL-001`), tenancy test (`TEST-001`), `DEC-002` eval start |
| 16–40 | Brand profile UI, content queue, approvals inbox, goal and plan UI | Agent runtime (`AI-001/002`), Clarity scoring, Muse generation, Sentinel minimal, Orbit planner | Weekly integration; eval set (`TEST-002`) |
| 41–60 | Dashboard (`ORB-002`), lead inbox UI | Lead form and scoring (`CON-001/002`), ManualPublish and Meta dev-mode connector (`MUS-002`) | `E2E-001`; staging (`DEPLOY-001`) |
| 61–75 | Polish, demo flow | Hardening, cost and failure tests | Pilot with a few real businesses, measure honestly, demo and report |

**Honest-claims rule for the demo and report:** state what is real, what uses test accounts, and what is mocked. Do not present mock data or the fake LLM provider as real results. Report real pilot numbers only.

**Cut order if time runs short:** Meta live connector (keep ManualPublish) → lead scoring polish → dashboard extras. Never cut approvals, tenancy tests, or the audit log.

---

## 12. Working with AI coding agents (founder-validates-own-code workflow)

1. Ask the agent for a **plan and small diff** per task; read the diff before accepting.
2. Ask it to explain any pattern you do not recognize; write or adapt the code yourself where you want to learn or own it.
3. Require tests with every change and the final report format in `CLAUDE.md` §11.
4. Never let an agent make architecture changes, run destructive commands, or deploy without your approval.
5. Keep sessions task-scoped; update `ACTIVE_TASKS.md` at the end of each.

---

## 13. Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| Queries return no rows | `app.workspace_id` not set in the transaction | Confirm `tenant_session` wraps the call; check RLS policy |
| Rows visible across workspaces | App connected as owner or `BYPASSRLS` role | Confirm role; confirm `FORCE ROW LEVEL SECURITY` |
| Duplicate posts or emails | Retry without idempotency check | Check external-ID-before-ack logic and `idempotency_key` |
| Tasks stuck in `running` | Worker crashed after claim | Add a reaper job that resets stale `running` tasks past a timeout |
| Plan rejected repeatedly | Model proposes actions outside the registry | Inspect validation errors; improve the planner prompt and eval |
| Cookie not sent from the web app | CORS or `SameSite`/domain mismatch | Check `WEB_ORIGIN`, `credentials: include`, cookie attributes |
| Costs spike | Missing budget check or loop | Check `agent_runs`; confirm step caps and budgets |

---

## 14. Definition of "ready to pilot"

All of: MVP loop passes e2e on staging; tenancy and approval-bypass tests pass; backup restore tested once; Sentry and alerts working; a written pilot consent note and data-handling note exist; owner can delete their workspace data; known issues recorded in `PROJECT_WARNINGS.md`.
