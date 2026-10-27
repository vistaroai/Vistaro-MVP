# CLAUDE.md — Vistaro AI Development Control File

> Mandatory instructions for every AI coding agent working on **Vistaro**.
> Read this file completely before touching any code. Last updated: 2026-10-18.

## 0. What this file is (and is not)

This file controls **how** you work: workflow, safety rules, verification, reporting.
It does not describe the whole product. Product knowledge lives in the files below. Read them; do not guess.

### File hierarchy (one source of truth per topic)

| File | Role | Path |
|---|---|---|
| `CLAUDE.md` | Rules and mandatory workflow | `/CLAUDE.md` |
| `docs/PROJECT_ROADMAP.md` | Complete phased roadmap, all tasks | `/docs/PROJECT_ROADMAP.md` |
| `docs/ACTIVE_TASKS.md` | Current queue plus the full ordered task sequence (no statuses) | `/docs/ACTIVE_TASKS.md` |
| `docs/TASK_PLAYBOOK.md` | Step-by-step instructions, checks and prompts for every task | `/docs/TASK_PLAYBOOK.md` |
| `docs/PROJECT_WARNINGS.md` | Warnings, risks, known bugs, technical debt | `/docs/PROJECT_WARNINGS.md` |
| `docs/ARCHITECTURE.md` | **Final** architecture, tech stack, ADR register, data model | `/docs/ARCHITECTURE.md` |
| `docs/DEVELOPMENT_GUIDE.md` | Step-by-step build guide, conventions, patterns, release and ops | `/docs/DEVELOPMENT_GUIDE.md` |
| `STARTUP_AI_MASTER_CONTEXT.md` | Full AI-oriented product and technical knowledge | repo root (intended path) |
| `STARTUP_MASTER_BLUEPRINT.md` | Human-oriented business and engineering rationale | repo root (intended path) |

Do not create duplicate or competing copies of these. If an equivalent file already exists in the repository, inspect and update it.

### Compatibility with `AGENTS.md`

If the repository uses `AGENTS.md` for shared agent instructions, keep it as a thin pointer to this file (see `AGENTS.md` in the delivery set). Do not maintain two divergent rule sets. If nested `CLAUDE.md` or `AGENTS.md` files exist in subfolders, read the ones relevant to the files you change; shared rules stay here.

### Status of the project at the time this file was written (verify before trusting)

- Vistaro is at the **bootstrap-complete stage**. `REPO-001` (2026-10-23) created the monorepo, minimal API and web shells, local compose file, CI workflow, and verified commands (see §12), and was merged into `main` via PR #1. No product feature is implemented; feature statements remain targets until their tasks are verified.
- No software feature is `DONE`. The architecture and technology stack are **decided** (see `docs/ARCHITECTURE.md`, finalized 2026-10-18 under the founders' delegation; the founders may change them through the process in §9). Pricing, first customer niche, tagline, and exact LLM model names are **still undecided**.
- If the repository now contains code, **the repository is the evidence of what exists**. Update the roadmap to match it (see §12).

---

## 1. Mandatory startup procedure

Run this sequence at the start of every session. Keep it proportional: for a one-line low-risk fix, steps 2 to 4 can be a few sentences.

### Step 1: Understand the project
1. Read this file.
2. Read `STARTUP_AI_MASTER_CONTEXT.md` (product, decisions, constraints, open questions), then `docs/ARCHITECTURE.md` (final design) and the relevant part of `docs/DEVELOPMENT_GUIDE.md`.
3. Consult `STARTUP_MASTER_BLUEPRINT.md` for rationale when needed.
4. If either master document is missing, say so and use only verified information. Do not reconstruct their content from memory.
5. Inspect the real repository: directory structure, configuration, dependency files, scripts, existing implementation, tests, CI.
6. Read nested `CLAUDE.md` / `AGENTS.md` files that apply to the area you will change.
7. **Never assume the documentation matches the code.**

### Step 2: Establish the current state
Determine, with evidence (file paths, command output):
- What is implemented, what works, what is incomplete, what is broken.
- What is in progress, and the next approved roadmap task.
- Whether there are uncommitted changes or other people's work to preserve (`git status`, `git diff --stat`, branch, recent log).
- Which components your work could affect.

**Never overwrite, reset, discard, stash-drop, or revert existing changes without explicit permission.**

### Step 3: Select the correct task
1. Read `docs/ACTIVE_TASKS.md`, then the task's entry in `docs/PROJECT_ROADMAP.md` (status and acceptance criteria) and its instructions in `docs/TASK_PLAYBOOK.md`. Task **status lives only in the roadmap**.
2. Check dependencies, priority, blockers, acceptance criteria.
3. Choose the highest-priority **READY** task appropriate to the request.
4. If the user asks for a different task, do that task, unless it conflicts with a critical safety rule or a documented dependency. If it does, explain and propose a safe path.
5. Do not start unrelated features because they seem useful.
6. If the next task is unclear, or a decision materially affects architecture, security, data integrity, or business direction, explain the uncertainty and ask.

### Step 4: Plan before substantial changes
State briefly: objective; affected files and components; approach; dependencies, risks, regressions; tests and acceptance criteria. Check `docs/PROJECT_WARNINGS.md` first (§7). Prefer the smallest reliable implementation.

### Step 5: Implement safely
- Follow existing architecture and conventions. Reuse existing components and patterns.
- No duplicate functionality, no unnecessary dependencies.
- Do not silently swap the stack. Do not ship placeholders as complete.
- Do not hardcode secrets. Do not weaken auth, authorization, validation, or tenant isolation to make something work.
- Keep changes focused. No unrelated refactoring.

### Step 6: Verify
- Run the repository's **actual** commands (discover them from package scripts, Makefile, CI config, README; never invent them).
- Check build, lint, types, tests, integration behavior where they apply.
- Verify API contracts, database compatibility, permissions, and error handling where affected.
- For AI features, test output quality, invalid input, uncertainty handling, failure cases, and fallbacks.
- **Never claim a check passed unless you ran it and saw it pass.** If you cannot run something, say why and what remains unverified.

### Step 7: Update project records
Update the task tracker and roadmap, implementation status and known limitations, architecture docs if a design decision changed, the decision log for newly approved decisions, new warnings or open questions, and record the tests actually run. Name the next recommended task.
**Completion requires acceptance criteria met and verification recorded, not merely code written.**

---

## 2. Product context you must not contradict

(Short form. The master documents are authoritative. Do not treat this section as a replacement for reading them.)

- **Vistaro** is an agentic AI platform for small-business growth and operations. Owner states a goal; **Orbit** plans; specialist modules execute; **Sentinel** enforces approvals.
- **Canonical modules:** Orbit (orchestration, workspace), Clarity (brand intelligence, AI visibility), Muse (content), Convert (leads/CRM), Market (store ops), Sentinel (permissions, approvals, audit), Pulse (performance, social listening), plus a core platform (auth, workspaces, integrations, RBAC, agent task runtime).
- **Earlier names** (Lens, Dream, Lead Master, Store Manager, Engagement Tracking) may appear in old notes. The mapping to canonical names is an unconfirmed inference (open question OQ-02). Use canonical names; mention the old name only for traceability.
- **Confirmed constraints:**
  - Consequential actions (publishing, outbound communication, financial actions) require configurable approval checks.
  - Orbit coordinates modules; it does not replace them.
  - Each module owns its domain data and workflows; access other modules' data through their interfaces.
  - Sentinel enforces permissions and approvals across the ecosystem.
  - Never fabricate market data, customers, metrics, or progress.
- **Stack (final, see `docs/ARCHITECTURE.md`):** modular monolith in a monorepo; Python 3.12 + FastAPI + SQLAlchemy + Alembic; React + TypeScript + Vite + Tailwind; PostgreSQL only (RLS for tenancy); Celery + Redis; own session auth; Sentinel in-process; custom planner-executor orchestration; provider-agnostic LLM layer (Anthropic default); Cloudflare Pages + Render + R2; GitHub Actions.
- **Team (2 people):** Anushka Varshney (frontend and platform lead), Dimple (AI and backend lead).
- **Working style:** the founder prefers to validate her own code over receiving wholesale replacement solutions. Prefer small, focused diffs with a clear explanation and tests. Offer to explain changes. Do not rewrite large working areas unprompted.

---

## 3. Non-negotiable engineering rules

1. **Inspect before modifying.** Never change code based on assumptions, summaries, or outdated docs.
2. **Preserve working functionality.** Identify affected dependencies; regression-test important existing flows.
3. **No unapproved architecture changes.** Do not replace databases, frameworks, major dependencies, auth systems, API contracts, or deployment infrastructure without an approved proposal (§9).
4. **No fabricated completion.** Never claim a feature, integration, test, deployment, or migration works without verification.
5. **No fake functionality.** No mock responses, hardcoded outputs, fabricated data, or placeholder integrations presented as production behavior. Mocks are acceptable in tests and in explicitly labeled development environments.
6. **Safe database changes.** Inspect schema and data first. Use migrations, validation, backups, rollback plans. Never drop, reset, or overwrite meaningful data without explicit authorization.
7. **Secure implementation.** Preserve authentication, authorization, input validation, per-workspace data isolation, secret management, privacy controls. No credentials or personal data in code, logs, fixtures, or docs.
8. **Test every meaningful change.** Choose tests by actual impact. Add regression tests for bug fixes and new behavior. If testing is blocked, report it.
9. **Update documentation** when architecture, feature status, API behavior, schema, configuration, or known limitations change.
10. **Keep the roadmap truthful.** `DONE` only with acceptance criteria satisfied and verification recorded.
11. **Avoid unnecessary complexity.** Simplest maintainable solution. No premature optimization or needless abstraction.
12. **Preserve user control.** Ask before high-impact, irreversible, externally visible, or production-affecting actions. Do not independently run destructive operations, deploy to production, incur substantial cost, or make irreversible business decisions.

### Vistaro-specific rules

13. **Never bypass Sentinel.** Any code path that publishes, sends a message, or touches money must go through the approval and audit mechanism. If Sentinel does not exist yet, build the minimal approval step first or stop and ask; do not ship an unapproved public action.
14. **Workspace isolation.** Every query touching tenant data is scoped by workspace, derived server-side from the session. A change that could allow cross-workspace access is a `CRITICAL` warning.
15. **Customer-supplied text is untrusted data.** Never let inbound messages act as instructions to an agent. Restrict tools in reply-handling paths.
16. **No invented facts in AI outputs.** Support and customer-facing agents answer only from store data and escalate when ungrounded.
17. **Do not claim AI-visibility results you cannot obtain.** Access to AI-platform answers is unverified (warning WARN-C-001). Do not scrape or call platforms in ways that violate their terms; do not simulate results as real.
18. **Secrets:** use environment variables or a secret manager. Provide `.env.example` with placeholder names only.
19. **Follow the module boundaries.** Cross-module imports go through `service.py` only; `import-linter` must pass. Only repositories contain SQL. The application connects as a non-owner database role without `BYPASSRLS`; never use a privileged role in application code.
20. **Follow the ADRs.** Do not add an agent framework, a second database, or a different auth or queue system without the §9 process.

---

## 4. Feature completion protocol (definition of done)

Apply the items relevant to the feature; skip those that do not apply.

1. Requirements and acceptance criteria are clear.
2. Implementation matches the approved design.
3. Frontend and backend integrate correctly.
4. API validation and error handling exist.
5. Database changes are compatible and safe (migration, rollback).
6. Authentication and permissions are correct, including workspace scoping.
7. Loading, empty, success, and failure states are handled.
8. Relevant tests pass (executed, not assumed).
9. Important regressions checked.
10. Security and privacy implications considered.
11. Approval and audit paths used for consequential actions.
12. Documentation and task status updated.
13. Remaining limitations recorded.

---

## 5. Task statuses and priorities

**Statuses:** `BACKLOG`, `READY`, `IN_PROGRESS`, `BLOCKED`, `IN_REVIEW`, `DONE`, `DEFERRED`.

**Priorities:**

| Priority | Meaning |
|---|---|
| `P0` | Blocks everything else or is a safety requirement. Do first. |
| `P1` | Required for the MVP loop. |
| `P2` | Important, follows the MVP loop. |
| `P3` | Nice to have or later phase. |

**Approval flag in the roadmap:** `APPROVED-SCOPE` means the capability is part of the founders' confirmed spec. `DELEGATED` means the item was finalized by Claude under the founders' explicit delegation on 2026-10-18; it is binding for planning unless the founders change it. Any new task you add yourself must be flagged `PROPOSED-TASK` (not approved) until the founders accept it.

---

## 6. Hierarchy of truth

1. Explicit, current instructions from the user for the current task (subject to safety rules).
2. Actual repository state, for what has been implemented.
3. Approved architecture decisions and current product requirements.
4. The current roadmap and active task tracker.
5. The master startup documents.
6. Older notes, proposals, and historical ideas.

Code proves what exists; it does not prove that a design choice was approved. If code conflicts with documented requirements, **report the discrepancy and propose a safe resolution**; do not copy either side blindly. An AI-generated suggestion is not an approved decision unless the founders explicitly accepted it.

---

## 7. Handling warnings

Before modifying a component, check `docs/PROJECT_WARNINGS.md`.

- **CRITICAL** warning affects the work: stop the unsafe action, explain the risk, propose a safe alternative, obtain approval where needed.
- **HIGH** warning affects the work: include it in the plan, explain how the change avoids worsening it or addresses it, test the relevant behavior.
- **MEDIUM / LOW:** assess relevance; do not expand scope unnecessarily.
- **New issue found:** record it in the register with evidence and a severity based on actual impact. Do not hide it because it is outside the current task.
- Never silently delete warnings. Close one only after the fix is verified; keep useful history.
- Distinguish **observed defects** from **preventive controls**. Do not invent bugs.

---

## 8. Repository verification and project health protocol

Discover real commands from `package.json` scripts, `pyproject.toml`, `Makefile`, `docker-compose` files, CI workflows, and READMEs. Do not assume they exist. Where applicable, check:

- Repository and branch state; uncommitted changes.
- Dependency installation and configuration.
- Required environment variables (names only, never values).
- Application startup; frontend build and lint; backend startup and tests.
- Database connectivity and schema compatibility.
- API health and integration behavior.
- LLM provider connectivity (without exposing keys or incurring large cost).
- Background jobs and scheduled tasks.
- Authentication and authorization behavior.
- Error logs and known warnings.
- Deployment configuration.

Report a concise health summary that separates **verified findings** from **checks not performed**. Not every check applies to every project.

---

## 9. Architectural change approval

Needs a written proposal **before** implementation: switching databases; replacing the frontend or backend framework; changing the auth strategy; adopting a major AI orchestration framework; changing a core API contract; reorganizing major modules; adding expensive infrastructure; changing how sensitive data is stored or processed.

The proposal states: current design; proposed change; why necessary; alternatives considered; migration and compatibility risks; implementation and test plan. After approval, record it in the decision log (in `STARTUP_AI_MASTER_CONTEXT.md` §2.6 until a dedicated ADR folder exists).
Small internal refactors do not need this process. Keep it proportional to risk.

**Decided (do not change without this process):** everything in the ADR register in `docs/ARCHITECTURE.md` (ADR-001 to ADR-020), including the stack, tenancy model, auth approach, job system, orchestration approach, hosting, and CI/CD.

**Still open (propose, do not assume):** exact LLM model names (`DEC-002`, needs evaluation), embeddings provider (`DEC-005`, Phase 3), payment gateway details beyond the Razorpay plan (`MKT-003`, verify), and anything marked **verify** in the architecture or guide. New architecture decisions are recorded as files under `docs/adr/`.

---

## 10. Documentation maintenance

When a change affects a documented area, make small, focused, traceable updates:
- Roadmap and active tasks (status, results).
- Warnings register (introduced, discovered, resolved).
- API docs when contracts change; data-model and migration docs when schemas change.
- Architecture diagrams when component relationships change.
- Setup instructions and environment-variable documentation (names only).
- Decision log for approved decisions.
- Test results and remaining limitations.

Do not rewrite the master documents for minor code changes. Do update them when a decision, architecture, or status they state becomes false.

---

## 11. Final report after every meaningful session

Use these headings:

1. **Objective**: what was requested and intended.
2. **Changes made**: files and components, with a brief explanation.
3. **Verification**: tests and checks actually executed, with results.
4. **Warnings and risks**: unresolved issues, new warnings, regressions.
5. **Roadmap status**: tasks completed, in progress, blocked.
6. **Next recommended action**: next highest-priority task and any prerequisite.
7. **Decisions required**: approvals or clarifications needed from the founders.

Be truthful. Do not say "all tests pass" if only a subset ran. Say what you did **not** verify.

---

## 12. First session in an existing repository

If the repository already contains code or documentation that the roadmap does not reflect:
1. Inspect the repository (§1 Step 1 and 2).
2. Record what exists in `docs/PROJECT_ROADMAP.md`, using status `IN_REVIEW` (implemented but not verified) rather than `DONE` until acceptance criteria are checked.
3. Replace the "no repository inspected" notes in these docs with verified facts.
4. Record real commands in a "Verified commands" section below.
5. Ask the founders to confirm anything that looks like an unapproved architectural choice.

### Verified repository state (REPO-001, 2026-10-23)

**Location:** `C:\Users\Anushka\OneDrive\Desktop\vistaromvp`
**Remote:** `origin` = `https://github.com/vistaroai/Vistaro-MVP.git`
**Branch:** `repo-001-bootstrap`, created from `main`; commit `4de4a31` "REPO-001: bootstrap monorepo"; follow-up docs commit `0cb9726` and docs note `29224b5`. Merged into `main` via PR #1 on 2026-10-23.
**Working tree:** clean at the tested commit. The bootstrap was re-tested from a fresh clone at `C:\Users\Anushka\AppData\Local\Temp\opencode\vistaro-repo001-clone`.

**Structure:** monorepo bootstrap. The repository now contains a minimal FastAPI service, a minimal React/Vite app, local service definitions, and a CI workflow. There are no product features, database migrations, authentication, Sentinel, or deployment configuration yet.

| Path | Role |
|---|---|
| `CLAUDE.md`, `AGENTS.md` | rules and agent pointer |
| `README.md` | fresh-clone quick start and checks |
| `STARTUP_*.md`, `Vistaro.docx` | product and business context |
| `docs/` | architecture, roadmap, active tasks, warnings, playbook |
| `docs/adr/` | ADR location; contains a format note only |
| `apps/api/` | `pyproject.toml`, `uv.lock`, `.python-version`, `src/vistaro`, `tests` |
| `apps/web/` | React 19 + TypeScript + Vite 8, Tailwind 4, Vitest, ESLint, Prettier |
| `infra/docker-compose.yml` | Postgres 16, Redis 7, Mailpit (unverified) |
| `.github/workflows/ci.yml` | backend, frontend, and secret-scan jobs |

**Docs layout:** the repository uses the verified `docs/` paths. The six reference documents moved from the repository root to `docs/`; `CLAUDE.md`, `AGENTS.md`, `README.md`, `STARTUP_*.md`, and `Vistaro.docx` stay at the root. WARN-G-009 is resolved.

**Verified commands** (run on 2026-10-23; from the workspace and repeated in the fresh clone where noted):

| Purpose | Command | Result |
|---|---|---|
| Install backend | `cd apps/api` then `uv sync` | Python 3.12.15; 77 packages; fresh clone passed |
| Run API (dev) | `cd apps/api` then `uv run uvicorn vistaro.main:app --reload --port 8000` | `/healthz` returned 200 `{"status":"ok","environment":"local"}` |
| Install frontend | `cd apps/web` then `pnpm install --frozen-lockfile` | 279 packages; fresh clone passed |
| Run web (dev) | `cd apps/web` then `pnpm dev` | `http://localhost:5173` returned 200; title `Vistaro` |
| Test backend | `cd apps/api` then `uv run pytest -q` | 1 passed; upstream Starlette deprecation warning about `httpx`/`httpx2` |
| Lint backend | `cd apps/api` then `uv run ruff check .` | All checks passed |
| Type-check backend | `cd apps/api` then `uv run mypy src` | No issues in 4 source files |
| Import boundaries | `cd apps/api` then `uv run lint-imports` | 1 contract kept, 0 broken |
| Lint frontend | `cd apps/web` then `pnpm lint` | Passed |
| Type-check frontend | `cd apps/web` then `pnpm typecheck` | Passed |
| Test frontend | `cd apps/web` then `pnpm test` | 1 file, 1 test passed |
| Build frontend | `cd apps/web` then `pnpm build` | Vite production build passed |
| Format check | `cd apps/web` then `pnpm format:check` | Passed |
| Migrate DB | - | No migrations until `DB-001` |
| Local services | `docker compose -f infra/docker-compose.yml up -d` | Not run; Docker is not installed. `INFRA-001` |
| CI | `.github/workflows/ci.yml` | Green on PR #1 (2026-10-23): backend, frontend, secret scan |

**YAML syntax:** `.github/workflows/ci.yml` and `infra/docker-compose.yml` parse with PyYAML. Parsing does not prove that GitHub Actions or Docker will run them.

**Versions:** Python 3.12.15, uv 0.13.5, Node.js 24.22.1, pnpm 12.15.0, TypeScript 5.9.3, Vite 8.3.5, FastAPI 0.161.1. The system Python is 3.15.1; `apps/api/.python-version` makes uv select 3.12.

**Environment:** uv was installed into the user Python scripts and exposed through `C:\Users\Anushka\AppData\Roaming\npm\uv.cmd`; pnpm 12.15.0 is global. PowerShell blocks `pnpm.ps1`; use `pnpm.cmd` or `Set-ExecutionPolicy -Scope Process Bypass` (documented in `README.md`). Docker is absent.

**Fresh-clone proof:** `git clone --branch repo-001-bootstrap` at `4de4a31`, then the README steps: copied `.env.example` to `.env`, `uv sync`, started the API, and got the health JSON above; ran `pnpm install --frozen-lockfile`, `pnpm dev`, and got HTTP 200. Both check suites passed in the clone.

**CI on PR #1 (GitHub-reported, 2026-10-23):** `Backend` passed in ~12s, `Frontend` in ~21s, `Secret scan` in ~8s. This is external verification recorded here because REPO-001 acceptance includes CI on a PR.

**Not verified:** staging (`INFRA-001`) and all product features.

### Verified database state (DB-001, 2026-10-23)

Docker Desktop 29.9.2 installed and running; `docker compose -f infra/docker-compose.yml up -d` verified (Postgres 16, Redis 7, Mailpit, all healthy). Container `vistaro-postgres-1`.

| Item | Verified result |
|---|---|
| `infra/initdb/01_roles_and_extensions.sql` | Created roles `vistaro_migrator`, `vistaro_app` (both `NOBYPASSRLS`, `rolbypassrls = f`, superuser = f) and extension `citext`; script is idempotent |
| `uv run alembic upgrade head` | From `apps/api`; migration `0001` ran as `vistaro_migrator`; tables owned by `vistaro_migrator` |
| `alembic downgrade -1` + `upgrade head` | Passed on empty DB and again on the same cycle with seeded rows |
| RLS on `memberships` | Enabled, forced, policy `tenant_isolation`; as `vistaro_app`: no setting → 0 rows; `set_config('app.workspace_id', …, true)` scoped to A → only A's row; insert for workspace B → policy violation; cross-tenant SELECT with WHERE → 0 rows |
| Schema | `users`, `workspaces`, `memberships` (role CHECK), `sessions` (`id_hash`, no workspace RLS per WARN-D-007), FK-ordered downgrade; no migration touched `vistaro_app` privileges beyond row CRUD |
| Backend checks on the branch | `ruff check .`, `mypy src`, `lint-imports`, `pytest -q` all pass |

**Design note:** roles/extensions are bootstrapped outside Alembic (creating roles requires privileges a migration role must not have); migrations run as `vistaro_migrator` via `MIGRATOR_DATABASE_URL`; the app will connect as `vistaro_app` via `DATABASE_URL`. Local passwords (`*_local_only`) are development-only and match the compose file.

**Not verified for DB-001:** nothing outstanding in DB-001 scope (the PR merged as PR #2 on 2026-10-24); pooled-connection reuse harness is `TEST-001`'s job, and any staging database belongs to `INFRA-001`.

### Verified tenancy harness (TEST-001, 2026-10-24)

| Item | Verified result |
|---|---|
| `src/vistaro/db/tenancy.py` | `sqlalchemy_url` pins psycopg 3; `set_tenant_scope` uses transaction-local `set_config('app.workspace_id', …, true)`; `TENANT_TABLE_WORKSPACE_COLUMNS` registry (new tenant tables must register here) |
| `tests/conftest.py` | Admin engine (seed/cleanup only) and app engine connecting exactly as `vistaro_app`; fixture truncates, seeds two workspaces, truncates after |
| `tests/test_tenancy.py` | 7 tests: unscoped sees zero rows; scoped sees only own rows; explicit cross-tenant filter returns zero; cross-tenant INSERT rejected by policy; pooled-connection reuse leaves no scope; generated per-table test for `memberships` |
| Sabotage proof | With `tenant_isolation` dropped on `memberships`, 3 tests fail (harness detects removed scoping); policy restored and tests pass again |
| Defect found and fixed | Migration `0002`: after a scoped transaction commits, the session GUC rests at `''` and the pre-0002 policy cast raised `InvalidTextRepresentation` instead of denying; `NULLIF(..., '')` now denies quietly. Down-verifiable (`downgrade -1` restores the old policy) |
| Backend checks on the branch | `ruff check .`, `mypy src`, `lint-imports`, `pytest -q` (7 passed) |

**CI change:** the backend job now runs a `postgres:16-alpine` service, applies `infra/initdb/01_roles_and_extensions.sql` via `docker exec`, runs `alembic upgrade head`, and exports the three local database URLs. Not yet observed on GitHub until this PR runs.

**Not verified for TEST-001:** nothing outstanding in TEST-001 scope (the PR merged as PR #3 on 2026-10-24); application-level tenancy wrappers arrive with `AUTH-002`, which must reuse `set_tenant_scope`.

### Verified API skeleton state (API-001, 2026-10-24)

**Branch:** `api-001-skeleton` (from `main` at `4fcb1255`). Not yet merged; awaiting founder review.
**Working directory:** `C:\Users\ASHVITA\Desktop\VistaroAI`
**Docker:** postgres, redis, mailpit all healthy via `docker compose -f infra/docker-compose.yml up -d`.

#### Files created / modified

| Path | Role |
|---|---|
| `apps/api/src/vistaro/core/errors.py` | `ErrorDetail`, `ErrorEnvelope` Pydantic models; typed exception hierarchy (`APIError`, `BadRequestError`, `UnauthorizedError`, `ForbiddenError`, `NotFoundError`, `ConflictError`, `ValidationFailedError`, `RateLimitedError`, `ServiceUnavailableError`); `register_error_handlers(app)` |
| `apps/api/src/vistaro/core/middleware.py` | `RequestIDMiddleware` (BaseHTTPMiddleware); `validate_request_id()` regex `^[a-zA-Z0-9_\-]{1,128}$`; structlog contextvars bind/unbind |
| `apps/api/src/vistaro/core/pagination.py` | `encode_cursor()`/`decode_cursor()` (base64url, sort-keyed JSON, max 1024 chars); `CursorPaginationParams`; `CursorPage[T]`; `paginate_results[T]()` |
| `apps/api/src/vistaro/core/idempotency.py` | `validate_idempotency_key()` regex `^[a-zA-Z0-9_\-\.:]{1,128}$`; `require_idempotency_key` and `optional_idempotency_key` FastAPI dependencies |
| `apps/api/src/vistaro/core/__init__.py` | Re-exports all new symbols from `core` |
| `apps/api/src/vistaro/main.py` | `register_error_handlers`, `RequestIDMiddleware`, CORS `expose_headers=["X-Request-ID"]`, `/healthz`, `/readyz`, `check_database()`, `check_redis()`, `readiness_checkers` (injectable for tests) |
| `apps/api/scripts/export_openapi.py` | Deterministic JSON export (sort_keys=True); run: `uv run python scripts/export_openapi.py` |
| `apps/api/openapi.json` | Generated OpenAPI spec committed to repo |
| `apps/api/tests/test_errors.py` | 10 contract tests for error envelope and exception hierarchy |
| `apps/api/tests/test_middleware.py` | 5 tests: ID generation, propagation, invalid/oversized rejection |
| `apps/api/tests/test_health.py` | 5 tests: liveness, readiness (healthy/degraded with injected checkers), no credential leaks |
| `apps/api/tests/test_pagination.py` | 11 tests: encode/decode roundtrip, malformed cursor, oversized, empty/under/at/over limit |
| `apps/api/tests/test_idempotency.py` | 10 tests: valid, missing, empty, invalid chars, length limits, FastAPI dependency |
| `apps/web/src/lib/api/schema.d.ts` | Generated TypeScript types from OpenAPI (via `openapi-typescript`) |
| `apps/web/src/lib/api/client.ts` | `createApiClient()` and default `api` instance using `openapi-fetch` |
| `apps/web/src/lib/api/client.test.ts` | 2 frontend contract tests |
| `apps/web/package.json` | Added `codegen:api` and `codegen:check` scripts |
| `.github/workflows/ci.yml` | Added `export-openapi` job (exports spec, verifies no drift vs committed `openapi.json`, uploads artifact); `frontend` job now depends on `export-openapi`, downloads artifact, and runs `codegen:check` |

#### Verification results (all run locally, 2026-10-24)

| Check | Command | Result |
|---|---|---|
| Backend lint | `cd apps/api && uv run ruff check .` | ✅ All checks passed |
| Backend type-check | `cd apps/api && uv run mypy src` | ✅ No issues in 10 source files |
| Import boundaries | `cd apps/api && uv run lint-imports` | ✅ 1 contract kept, 0 broken |
| Backend tests | `cd apps/api && uv run pytest -q` | ✅ 47 passed, 1 warning (Starlette httpx deprecation) |
| Frontend lint | `cd apps/web && pnpm lint` | ✅ Passed |
| Frontend type-check | `cd apps/web && pnpm typecheck` | ✅ Passed |
| Frontend tests | `cd apps/web && pnpm test` | ✅ 3 passed (2 test files) |
| Frontend build | `cd apps/web && pnpm build` | ✅ Passed |
| Baseline drift check | `cd apps/web && pnpm codegen:check` | ✅ Exited 0 (no drift) |
| **Negative drift test** | Appended sentinel comment to `schema.d.ts`, ran `pnpm codegen:check` | ✅ Exited 1 ("Generated types are not up-to-date!") |
| Restore after drift | `pnpm codegen:api` then `pnpm codegen:check` | ✅ Exited 0 (restored, no residual drift) |
| OpenAPI export | `cd apps/api && uv run python scripts/export_openapi.py` | ✅ `openapi.json` regenerated deterministically |
| Git openapi drift | `git diff apps/api/openapi.json` | ✅ No diff (file is untracked-new, not modified) |

**Status update:** API-001 was merged to `main` via PR #4 at `85d800d` on 2026-10-24. Its local acceptance checks were recorded above. GitHub Actions results for PR #4 were not independently rechecked during SEC-001.

**Security notes:** Request IDs validated and bounded (max 128 chars, alphanumeric+`_-` only). Health endpoints return no credentials, stack traces, or connection strings. Idempotency helper is a key validator and dependency only — no cross-request persistence claim. Cursor encoding is base64url with bounded JSON, no SQL or raw offsets exposed.

**No new tenant tables introduced.** No import-linter contracts broken.

### Verified security baseline state (SEC-001, 2026-10-24)

**Branch:** `sec-001-security-baseline`, created from clean `main` at `85d800d`. No commits, push, merge, deployment, authentication flow, or session issuance.

| Control | Implementation and local evidence |
|---|---|
| CSRF | `GET /csrf` issues an unpredictable one-hour double-submit token cookie and returns the token without caching. Unsafe methods require the exact configured `WEB_ORIGIN`, matching cookie and `X-CSRF-Token`; safe methods pass. Tests cover missing/mismatched token, wrong origin, and valid token. The web API client adds the header when supplied a `getCsrfToken` callback and only sends it to the configured API origin. AUTH-001 must bind CSRF validation to the authenticated session. |
| Cookie defaults | `session_cookie_options` returns `HttpOnly`, `Secure` outside local, and `SameSite=Lax` locally / `None` for staging and production (cross-site Pages-to-API deployment); tested. No session cookie is issued in this task. CSRF cookie is readable by design and has `Path=/`, `Max-Age=3600`, secure environment flags. |
| Headers | CSP, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and `Permissions-Policy` apply to success and error responses. HSTS is set only for `APP_ENV=staging` or `production`; local and test environments omit it. |
| Rate limiting | Redis Lua fixed-window counter; default 120 requests per direct ASGI peer per 60 seconds. Returns 429 with `Retry-After` and limit headers; returns 503 on Redis errors; `/healthz` and `/readyz` are exempt. `X-Forwarded-For` is not trusted. Tests cover threshold, reset, forwarded-header spoofing, health exemption, backend failure, and invalid configuration. |
| Dependency and secret checks | CI adds `uv audit --locked` and `pnpm audit --prod --audit-level=high`; TruffleHog remains in CI, now reports verified and unknown findings. Local audits observed no known vulnerabilities. Dependabot version updates were disabled on 2026-10-28 (founders' request: no bot-authored commits); bumps are done manually. |

**Verification results (2026-10-24):**

| Check | Result |
|---|---|
| `uv run ruff check .` | Passed |
| `uv run mypy src` | Passed; 12 source files |
| `uv run lint-imports` | Passed; 1 contract kept, 0 broken |
| `uv run pytest -q` | Passed; 61 tests. Existing Starlette/httpx deprecation warning remains. |
| `uv run python scripts/export_openapi.py` | Passed; deterministic OpenAPI regenerated with LF line endings |
| `uv audit --locked` | Passed; no known vulnerabilities/adverse statuses in 77 packages. uv 0.13.4 reported this command is experimental. |
| `pnpm.cmd lint` / `typecheck` / `test` / `build` | Passed; 6 frontend tests |
| `pnpm.cmd format:check` / `codegen:check` | Passed |
| `pnpm.cmd audit --prod --audit-level=high` | Passed; no known vulnerabilities |
| CI and Dependabot YAML parse | Passed using PyYAML |
| `git diff --check` | Passed |

**Not run:** GitHub Actions and TruffleHog on this branch (the branch was not pushed and no PR was opened); no staging or browser-based deployment test; repository-level GitHub advisory settings were not inspected. The first npm audit attempt failed DNS in the sandbox; the elevated rerun succeeded with no known vulnerabilities.

**Limitations:** hosted proxy behavior is not verified (`WARN-E-007`); all users sharing one direct proxy peer may share a rate-limit bucket. Redis is required for non-health routes and the limiter fails closed. The fixed-window approach can burst across a window boundary. The CI TruffleHog action still references mutable `@main`, as it did before this task. `AUTH-001` must consume the tested session cookie defaults, and `UI-001` must fetch/store the `/csrf` token and provide the client callback.

**Task status:** SEC-001 was merged into `main` via PR #5 on 2026-10-25 and independently verified on 2026-10-27 (see below); it is `DONE`.

---

### Independent audit of API-001 and SEC-001 (main, 2026-10-27)

Ran on `main` at the PR #5 merge with local services up: `ruff` clean, `mypy src` clean (12 files), `lint-imports` kept, `pytest` **61/61 passed** (47 API-001-era + security), frontend `lint`/`typecheck`/`build` exit 0 and Vitest 6/6, `scripts/export_openapi.py` produces no diff against the committed `openapi.json`. Live server smoke on port 8002 verified: `/healthz` 200, `/readyz` `ok` with `database: ok, redis: ok`, `X-Request-ID` set and propagated, CSP/`X-Frame-Options`/`X-Content-Type-Options`/`Referrer-Policy`/`Permissions-Policy` present, 404 body is the standard error envelope, and a valid `/csrf` token + matching `Origin` + `X-CSRF-Token` header passes the CSRF middleware.

**Found and fixed:** `build_engine` (vistaro/db/tenancy.py) set no `connect_timeout`; psycopg/libpq hangs indefinitely when Postgres is unreachable, so `/readyz` hung forever and pytest hung instead of skipping when services were down. Fix: `connect_args={"connect_timeout": 5}` on every engine (WARN-B-013). With services down, `/readyz` now returns 503 quickly.

**Noted, not changed:** the Redis rate limiter fails **closed** (503 on all non-health routes when Redis is down) — founders should confirm this availability trade-off. `check_database()` builds a throwaway engine per readiness call (minor; OBS-001/AUTH-002 can pool it). Ops: Docker Desktop is a user-space install at `%LOCALAPPDATA%\Programs\DockerDesktop\Docker Desktop.exe` and must be running before any local API work.

### AUTH-001 Phase A (branch `auth-001-email-session`, 2026-10-28)

Implemented email signup/login/logout/verification and server-side sessions, per the plan approved by the founders (Google sign-in deferred to Phase B pending OAuth credentials). `ruff`, `mypy`, `lint-imports` clean; pytest **88/88** (27 new auth tests); `alembic upgrade/downgrade/upgrade` verified for migration `0003`; OpenAPI re-exported with no drift (`openapi.json` + regenerated `apps/web/src/lib/api/schema.d.ts`); frontend lint/typecheck/build exit 0 and vitest green; live smoke on port 8000: signup → real Mailpit email at `localhost:8025` → verify link → `/auth/me` shows verified → logout with bound CSRF.

Key decisions recorded during build:
- Tokens (session cookie value and verification link) exist only as SHA-256 digests in the DB (`services/tokens.py`); sessions stay outside RLS scopes and are resolved by user, hashed only (WARN-D-007 note).
- Login and all verification-link failures return one shared generic envelope; unknown accounts burn the same Argon2id work via `DUMMY_HASH` (`services/passwords.py`).
- `GET /csrf` re-binds the token to a live session (`api/deps.py::rebind_session_csrf`) — found via live smoke because a mid-session refetch would otherwise poison logout.
- Test emails use `@example.com` because `email-validator` rejects reserved `.test` domains; `EMAIL_VALIDATOR` dependency added.
- `conftest.py` raises the rate limit for the whole test process; limiter thresholds are still tested separately with dedicated mini-apps.

---

## 13. Keeping this file small

This file holds rules and workflow only. If it grows, split detail into focused files under `docs/` and link them here. Avoid circular references and duplicated policies. For multi-app repositories, add local `CLAUDE.md` files per app and keep shared rules here.
