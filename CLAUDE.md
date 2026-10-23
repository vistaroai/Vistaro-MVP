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

- Vistaro is at the **bootstrap stage**. `REPO-001` (2026-10-23) created the monorepo, minimal API and web shells, local compose file, CI workflow, and verified commands (see §12). No product feature is implemented; feature statements remain targets until their tasks are verified.
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
**Branch:** `repo-001-bootstrap`, created from `main`; commit `4de4a31` "REPO-001: bootstrap monorepo"; a follow-up docs-only commit records verification. Local only; not pushed.
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
| `.github/workflows/ci.yml` | backend, frontend, and secret-scan jobs (not yet run on GitHub) |

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
| CI | `.github/workflows/ci.yml` | Not run on GitHub; must pass on the first PR |

**YAML syntax:** `.github/workflows/ci.yml` and `infra/docker-compose.yml` parse with PyYAML. Parsing does not prove that GitHub Actions or Docker will run them.

**Versions:** Python 3.12.15, uv 0.13.5, Node.js 24.22.1, pnpm 12.15.0, TypeScript 5.9.3, Vite 8.3.5, FastAPI 0.161.1. The system Python is 3.15.1; `apps/api/.python-version` makes uv select 3.12.

**Environment:** uv was installed into the user Python scripts and exposed through `C:\Users\Anushka\AppData\Roaming\npm\uv.cmd`; pnpm 12.15.0 is global. PowerShell blocks `pnpm.ps1`; use `pnpm.cmd` or `Set-ExecutionPolicy -Scope Process Bypass` (documented in `README.md`). Docker is absent.

**Fresh-clone proof:** `git clone --branch repo-001-bootstrap` at `4de4a31`, then the README steps: copied `.env.example` to `.env`, `uv sync`, started the API, and got the health JSON above; ran `pnpm install --frozen-lockfile`, `pnpm dev`, and got HTTP 200. Both check suites passed in the clone.

**Not verified:** CI on GitHub (no push/PR), Docker Compose (Docker absent), staging (`INFRA-001`), database migrations (`DB-001`), and all product features.

---

## 13. Keeping this file small

This file holds rules and workflow only. If it grows, split detail into focused files under `docs/` and link them here. Avoid circular references and duplicated policies. For multi-app repositories, add local `CLAUDE.md` files per app and keep shared rules here.
