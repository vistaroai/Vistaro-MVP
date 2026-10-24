# ACTIVE TASKS — Vistaro

Execution queue and full ordered task sequence. Definitions and acceptance criteria: `/docs/PROJECT_ROADMAP.md`. Step-by-step instructions per task: `/docs/TASK_PLAYBOOK.md`. Rules: `/CLAUDE.md`.
Last updated: 2026-10-23 · Cycle: **Cycle 0 — Bootstrap and validation**

> Status words match the roadmap. If this file and the roadmap disagree, the roadmap wins; fix this file.

## Current task

Handover: the next tasks are picked up by another teammate. Nothing is in
progress right now; the ordered queue below is the handoff.

| ID | Task | Status | Owner | Why now |
|---|---|---|---|---|
| -- | (none in progress) | -- | -- | `TEST-001` merged via PR #3 and queue handed to a teammate |

## Next actionable tasks (in order)

| # | ID | Task | Depends on | Status | Notes |
|---|---|---|---|---|---|
| 1 | API-001 | API skeleton: error envelope, request IDs, health endpoints, OpenAPI | DB-001 | READY | |
| 2 | SEC-001 | Security baseline: CSRF, cookie flags, headers, rate limiting | DB-001 | READY | |
| 3 | AUTH-001 | Signup, login, sessions, email verification | DB-001, SEC-001 | BLOCKED | Waits on `SEC-001` |
| 4 | INFRA-001 | Local docker-compose and staging; verify hosting plan and `pgvector` | REPO-001 | READY (local half verified) | Staging remains: Render, Cloudflare Pages, secrets |

## Parallel non-code tasks (can start now)

| ID | Task | Status | Notes |
|---|---|---|---|
| VAL-001 | Interview real business owners | READY | Needed for the SEVA submission and for choosing the niche. Decide the interview count first |
| DOC-001 | Confirm module-name mapping; share full Product Features report | READY | Needs the founders |
| NAME-001 | Check the name Vistaro (web, domains, handles, trademark, app stores) | READY | |
| RES-001 | Research legal access to AI-platform answers | READY | Decides whether AI-visibility is built |
| LEGAL-001 | Advice on data protection and messaging consent | READY | |
| SEVA-001 | Finish SEVA Stage 1 deck and dossier with real evidence | READY | **Deadline unknown. Founders to supply it** |

## Blockers and dependencies right now

| Blocker | Affects | Needed from |
|---|---|---|
| Docker Compose Postgres is verified locally; the staging half of `INFRA-001` (Render, Cloudflare Pages, secrets) is untouched | `INFRA-001` | Create staging accounts and verify plan, region, `pgvector` during `INFRA-001` |
| SEVA deadline unknown | `SEVA-001` priority | Founders |
| Full Product Features report not seen | `DOC-001` | Founders |
| Hosting plan and region unverified | `INFRA-001` | Verification during `INFRA-001` |

## Awaiting decisions

| Decision | Reference | Who |
|---|---|---|
| First niche | `VAL-002` (after interviews) | Founders |
| Module-name mapping confirmation | `DOC-001`, WARN-G-001 | Founders |
| LLM model names and tiers | `DEC-002` (after `AI-002`, `TEST-002`) | Founders, informed by evaluation |
| Pricing and tagline | Roadmap section 2 | Founders (later) |

## Recently completed

| Date | Item | Note |
|---|---|---|
| 2026-10-23 | `REPO-001` monorepo bootstrap | Created apps/api, apps/web, infra, CI; fresh clone verified; CI green on PR #1. State recorded in `CLAUDE.md` §12 |
| 2026-10-23 | `REPO-000` repository inspection | Docs-only repository on `main`; no application code or runnable app commands. State recorded in `CLAUDE.md` §12 |
| 2026-10-23 | Local tooling | Installed uv 0.13.5 and Python 3.12.15 (via uv); pnpm 12.15.0; Docker Desktop 29.9.2 installed 2026-10-23 |
| 2026-10-23 | `DB-001` base schema | Roles + `citext` via `infra/initdb/`, Alembic `users`/`workspaces`/`memberships`/`sessions`, forced RLS on `memberships`; all acceptance checks verified locally. See `CLAUDE.md` §12 |
| 2026-10-24 | `DB-001` merged into `main` via PR #2 | Task marked DONE in the roadmap |
| 2026-10-24 | `TEST-001` tenancy harness | Isolation tests, pooled-connection proof, sabotage check; caught and fixed the unset-scope policy defect (migration `0002`); CI gained a Postgres service. Merged via PR #3 |
| 2026-10-18 | `DEC-001` stack and architecture | Decided under founders' delegation; see `ARCHITECTURE.md` |
| 2026-10-18 | `DEC-003` minimal approval in Phase 1 | Yes |
| 2026-10-18 | `DEC-004` competitor watch in Pulse | Yes |

`DB-001` is merged and the only build task marked DONE with evidence. **Do not mark any build task done without verification** (`CLAUDE.md` §4).

## Next recommended action

Start `TEST-001` now (the tenancy test harness). In parallel: `INFRA-001` staging part, and the non-code tasks `VAL-001`/`DOC-001`.

## Full execution sequence (all tasks, in order)

Every task in the roadmap, in the order to do them. **Status is not repeated here** (see the roadmap; it is the single source of truth). **Instructions for each task** are in `/docs/TASK_PLAYBOOK.md`. Run the session protocol in the playbook §1 for each one.

### Track A: non-code, start now, in parallel

| # | ID | Task |
|---|---|---|
| 1 | `REPO-000` | Inspect the repository |
| 2 | `DOC-001` | Reconcile names and the feature report |
| 3 | `VAL-001` | Interview real business owners |
| 4 | `NAME-001` | Check the name |
| 5 | `RES-001` | AI-platform access research |
| 6 | `LEGAL-001` | Legal advice |
| 7 | `SEVA-001` | Finish the SEVA Stage 1 submission |
| 8 | `VAL-002` | Choose the first niche |

### Decisions already made (no work needed)

| # | ID | Task |
|---|---|---|
| 9 | `DEC-001` | Stack and hosting (decided) |
| 10 | `DEC-003` | Minimal approval step in Phase 1 (decided) |
| 11 | `DEC-004` | Competitor watch lives in Pulse (decided) |

### Wave B: foundation

| # | ID | Task |
|---|---|---|
| 12 | `REPO-001` | Create the repository |
| 13 | `INFRA-001` | Local services and staging |
| 14 | `DB-001` | Roles, extensions, base schema |
| 15 | `TEST-001` | Tenancy test harness |
| 16 | `API-001` | API skeleton |
| 17 | `SEC-001` | Security baseline |
| 18 | `OBS-001` | Observability and cost recording |
| 19 | `UI-001` | Web app shell |

### Wave C: identity and tenancy

| # | ID | Task |
|---|---|---|
| 20 | `AUTH-001` | Authentication |
| 21 | `AUTH-002` | Workspaces and tenant scoping |
| 22 | `AUTH-003` | Roles and permissions |

### Wave D: platform

| # | ID | Task |
|---|---|---|
| 23 | `INT-001` | Connector framework |
| 24 | `AI-001` | Agent task runtime |
| 25 | `AI-002` | LLM client and structured output |
| 26 | `TEST-002` | AI evaluation harness |
| 27 | `DEC-002` | Confirm LLM provider and model tiers |

### Wave E: modules

| # | ID | Task |
|---|---|---|
| 28 | `CLA-001` | Brand profile |
| 29 | `CLA-002` | Brand scoring |
| 30 | `SEN-001` | Minimal Sentinel |
| 31 | `MUS-001` | Content generation |
| 32 | `INT-003` | ManualPublish connector |
| 33 | `MUS-002` | Scheduling and publishing |
| 34 | `ORB-001` | Goals and plans |
| 35 | `ORB-002` | Orbit dashboard |
| 36 | `CON-001` | Lead form and inbox |
| 37 | `CON-002` | Pipeline and lead scoring v1 |
| 38 | `INT-002` | Meta Graph connector (development mode) |

### Wave F: delivery (completes the MVP)

| # | ID | Task |
|---|---|---|
| 39 | `E2E-001` | End-to-end loop |
| 40 | `DEPLOY-001` | Staging pipeline and rehearsal |

### Phase 1-S: SEVA window (only if selected)

| # | ID | Task |
|---|---|---|
| 41 | `SEVA-002` | Map the 75 days |
| 42 | `SEVA-003` | Pilot and honest report |

### Phase 2

| # | ID | Task |
|---|---|---|
| 43 | `SEN-002` | Full policies and audit viewer |
| 44 | `API-002` | Server-Sent Events |
| 45 | `CON-003` | Conversations and follow-up agent |
| 46 | `MKT-001` | Catalog and orders |
| 47 | `MKT-002` | Inventory and low-stock signals |
| 48 | `MKT-003` | Razorpay payments |
| 49 | `PUL-001` | Engagement tracking |
| 50 | `CLA-003` | AI-visibility tracking |
| 51 | `CLA-004` | Content-fix recommendations |
| 52 | `OBS-002` | Alerts |

### Phase 3

| # | ID | Task |
|---|---|---|
| 53 | `DEC-005` | Embeddings provider (Phase 3) |
| 54 | `ORB-003` | Cross-module orchestration |
| 55 | `ORB-004` | Shared memory |
| 56 | `MKT-004` | Support agent |
| 57 | `CON-005` | Reply handling |
| 58 | `MUS-003` | Auto-generated visibility fixes |
| 59 | `TEST-003` | Expanded evals |

### Phase 4

| # | ID | Task |
|---|---|---|
| 60 | `PUL-002` | Forecasting baseline |
| 61 | `PUL-003` | Automated experiments |
| 62 | `PUL-004` | Anomaly alerts |
| 63 | `PUL-005` | Competitor and market watch |
| 64 | `ORB-005` | Weekly summary and ops alerts |
| 65 | `CON-006` | Booking |
| 66 | `CON-007` | Re-engagement |
| 67 | `CON-008` | WhatsApp (deferred) |

### Phase 5

| # | ID | Task |
|---|---|---|
| 68 | `SEC-002` | Security review |
| 69 | `PERF-001` | Load and cost tests |
| 70 | `BILL-001` | Billing |
| 71 | `OPS-001` | Runbooks and drills |
| 72 | `BETA-001` | Beta onboarding |
| 73 | `DEPLOY-002` | Production hardening and go/no-go |

## How to update this file

At the end of every session: move finished work to "Recently completed" (keep the last ~10), promote the next READY tasks, refresh blockers and awaiting-decision lists, and set the date. Keep the top sections (current task, next tasks, blockers) short; the sequence at the bottom changes only when tasks are added or reordered.
