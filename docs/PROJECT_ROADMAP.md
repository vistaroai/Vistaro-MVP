# PROJECT ROADMAP — Vistaro (FINAL, whole roadmap)

Version 2.0 · 2026-10-18. Supersedes the 2026-10-17 draft.
Rules: `/CLAUDE.md`. Current queue and ordered sequence: `/docs/ACTIVE_TASKS.md`. Instructions per task: `/docs/TASK_PLAYBOOK.md`. Risks: `/docs/PROJECT_WARNINGS.md`. **This file is the single source of truth for task status.**
Design: `/docs/ARCHITECTURE.md`. How to build: `/docs/DEVELOPMENT_GUIDE.md`. Product context: `STARTUP_AI_MASTER_CONTEXT.md`.

## 1. Authority and honesty

- On 2026-10-18 the founders delegated to Claude the finalization of the architecture, tech stack, and this roadmap. Items finalized under that delegation carry approval flag `DELEGATED`; the founders may change any of them. Items from the founders' own confirmed spec carry `APPROVED-SCOPE`.
- `REPO-000` inspected the repository on 2026-10-23 and `REPO-001` created the monorepo bootstrap. The only verified software is that bootstrap; no product feature is `DONE`.
- Bootstrap paths are verified in `CLAUDE.md` §12. Feature paths are filled in when each task starts; use `docs/ARCHITECTURE.md` §3 as the intended layout.

## 2. Current stage and status summary

| Item | State |
|---|---|
| Stage | `REPO-001`, `DB-001`, `TEST-001`, and `API-001` DONE (merged via PRs #1-#4). `SEC-001` `IN_REVIEW` on `sec-001-security-baseline`; local checks recorded in `CLAUDE.md` §12; founder review and PR CI remain. |
| Competition | DTU SEVA 2026, Stage 1 (deadline: **unknown**, see ACTIVE_TASKS) |
| Team | Anushka Varshney (frontend and platform), Dimple (AI and backend) |
| Stack | Bootstrap toolchain verified (FastAPI, React/Vite, uv, pnpm); database, Redis, workers, hosting, and integrations unverified |
| First niche, pricing, tagline | Undecided |

| Category | Items |
|---|---|
| 1. Completed and verified | Decisions `DEC-001`, `DEC-003`, `DEC-004`; `REPO-000`; `REPO-001`; `DB-001`; `TEST-001`; `API-001` |
| 2. Implemented but not fully verified | `SEC-001` (implementation and local checks recorded; founder review and PR CI pending) |
| 3. In progress | None |
| 4. Ready to implement | `INFRA-001`, `OBS-001`, `UI-001`, `AI-001`, `DOC-001`, `VAL-001`, `NAME-001`, `RES-001`, `LEGAL-001`, `SEVA-001` |
| 5. Blocked | `AUTH-001` (waits on `SEC-001`); the rest of Phase 1; `VAL-002`; `CLA-003` waits on `RES-001` |
| 6. Planned for later | Phases 2 to 5 |
| 7. Still undecided | First niche, pricing, tagline, embeddings provider (`DEC-005`), LLM model names (`DEC-002` evaluation), name clearance |

## 3. Definitions

**Statuses:** `BACKLOG`, `READY`, `IN_PROGRESS`, `BLOCKED`, `IN_REVIEW`, `DONE`, `DEFERRED`. A task whose predecessor is unfinished is `BLOCKED`; it becomes `READY` automatically when predecessors are `DONE`.
**Priorities:** `P0` blocks everything or is a safety requirement; `P1` required for the MVP loop; `P2` important after the MVP loop; `P3` later or optional.
**Approval flags:** `APPROVED-SCOPE` (founders' confirmed spec); `DELEGATED` (finalized by Claude under the founders' 2026-10-18 delegation; changeable).
**ID prefixes:** `VAL` validation, `NAME` naming, `DOC` docs, `RES` research, `LEGAL` legal, `DEC` decision, `SEVA` competition, `REPO` repo, `INFRA` infrastructure, `DB` database, `AUTH` identity and tenancy, `API` API, `INT` integrations, `AI` agent runtime and LLM, `CLA` Clarity, `MUS` Muse, `CON` Convert, `MKT` Market, `SEN` Sentinel, `PUL` Pulse, `ORB` Orbit, `UI` frontend, `TEST` testing, `OBS` observability, `SEC` security, `PERF` performance, `BILL` billing, `OPS` operations, `BETA` beta, `DEPLOY` deployment.

## 4. MVP definition

One complete loop, all steps real (test accounts allowed where stated):

> Owner states a goal → Orbit proposes a plan → owner approves → Muse drafts on-brand content → Clarity scores it → owner approves through Sentinel → content is published (ManualPublish, and Meta in development mode if available) → a lead arrives through the lead form and is scored → Orbit reports progress.

**Out of the MVP:** AI-visibility tracking, Market, Pulse, shared memory, automated follow-ups, WhatsApp, booking.
**MVP acceptance (binary):** the loop completes in staging with real data; every public action is approval-gated and audited; tenancy and approval-bypass tests pass; a restore from backup has been tested once.

## 5. Phases and critical path

| Phase | Name | Source | Status |
|---|---|---|---|
| 0 | Validation, decisions, definition | Delegated | In progress (decisions done; research tasks ready) |
| 1 | Core platform and MVP loop | Spec + delegated breakdown | Blocked on `REPO-001` |
| 1-S | SEVA prototype window (75 days, only if selected) | Delegated | Backlog |
| 2 | Market, Pulse basics, Sentinel full, follow-ups, visibility | Spec | Backlog |
| 3 | Goal-driven orchestration, shared memory, support agent | Spec | Backlog |
| 4 | Advanced automation | Spec | Backlog |
| 5 | Beta, hardening, launch | Delegated | Backlog |

**Critical path:** `REPO-000` → `REPO-001` → `DB-001` → `AUTH-001/002` → `TEST-001` → `AI-001/002` → `CLA-001/002` → `MUS-001` + `SEN-001` → `MUS-002` → `ORB-001` → `ORB-002` → `CON-001/002` → `E2E-001` → `DEPLOY-001`.

---

## 6. Phase 0: validation, decisions, definition

| ID | Objective and value | Depends on | Acceptance criteria | Required tests / verification | Pri | Status | Approval |
|---|---|---|---|---|---|---|---|
| REPO-000 | Find and inspect the real repository if any; record structure and verified commands in `CLAUDE.md` §12 | none | Location, branch, tree, commands recorded, or "none exists" recorded | Commands actually run | P0 | DONE (inspected 2026-10-23: docs-only repository; no application code or runnable app commands; state recorded in `CLAUDE.md` §12) | DELEGATED |
| DOC-001 | Founders confirm old-to-new module name mapping; share full *Product Features & Functional Responsibilities Report*; reconcile docs | founders | Mapping confirmed in writing; master docs diffed against report | Founder review | P0 | READY | DELEGATED |
| VAL-001 | Interview real owners with a written script; capture quotes and numbers | none | Interview count set beforehand and met; notes stored; pains ranked from evidence | Coverage vs script | P0 | READY | DELEGATED |
| VAL-002 | Choose first niche | VAL-001 | Niche recorded in decision log | Founder sign-off | P0 | BLOCKED | DELEGATED |
| NAME-001 | Check "Vistaro": web, domains, handles, trademark classes 9/35/42, app stores | none | Dated results; go/no-go | Searches run | P1 | READY | DELEGATED |
| RES-001 | Research legal, reliable access to AI-platform answers per platform | none | Per-platform access method and terms summarized with sources and dates | Sources cited | P1 | READY | DELEGATED |
| LEGAL-001 | Qualified advice on data protection, messaging consent, retention | none | Written constraints recorded in warnings register | Advisor input recorded | P1 | READY | DELEGATED |
| DEC-001 | Stack and hosting | none | ADR register in `ARCHITECTURE.md`; `CLAUDE.md` §9 updated | Review of docs | P0 | DONE (delegated 2026-10-18) | DELEGATED |
| DEC-002 | Confirm LLM provider and model tiers by evaluation | AI-002, TEST-002 | Fixed task set run on candidates; choice and costs recorded | Evaluation executed | P1 | IN_REVIEW (default chosen: provider-agnostic, Anthropic default; evaluation pending) | DELEGATED |
| DEC-003 | Minimal approval step ships in Phase 1 | none | Recorded: **yes**, because approvals are mandatory for public actions | n/a | P0 | DONE (delegated 2026-10-18) | DELEGATED |
| DEC-004 | Competitor monitoring lives in Pulse | none | Recorded: **Pulse**, feeding Clarity and Muse through services | n/a | P3 | DONE (delegated 2026-10-18) | DELEGATED |
| DEC-005 | Embeddings provider for retrieval | Phase 3 start | Candidates compared on multilingual (Hindi and English) quality and cost | Evaluation executed | P2 | BACKLOG | DELEGATED |
| SEVA-001 | Finish SEVA Stage 1 deck and 12-point dossier with real evidence, two-person team, canonical names | VAL-001, DOC-001 | Official template, under 20 MB; every required point filled; assumptions labeled | Checked against rubric | P0 | READY | DELEGATED |

---

## 7. Phase 1: core platform and MVP loop

### 7.1 Foundation

| ID | Objective and value | Depends on | Acceptance criteria | Required tests | Pri | Status | Approval |
|---|---|---|---|---|---|---|---|
| REPO-001 | Create monorepo, CI, `.env.example`, README with verified commands | REPO-000, DEC-001 | Fresh clone runs both apps from README; CI runs on a PR; no secrets in history | Fresh-clone test; secret scan | P0 | DONE (fresh clone verified; CI green on PR #1, 2026-10-23) | DELEGATED |
| INFRA-001 | Local docker-compose; staging on Render and Cloudflare Pages; secrets configured; **verify** plan, region, `pgvector` availability | REPO-001 | Staging reachable; secrets only in platform store; findings recorded | Smoke test; secret scan | P0 | READY | DELEGATED |
| DB-001 | Roles, extensions, base schema and migrations (`users`, `workspaces`, `memberships`, `sessions`) with RLS on tenant tables | REPO-001 | Up and down migrations pass on empty and seeded DB; roles correct (`vistaro_app` has no `BYPASSRLS`) | Migration tests | P0 | DONE (verified locally and merged via PR #2, 2026-10-24) | DELEGATED |
| API-001 | API skeleton: error envelope, request IDs, health endpoints, OpenAPI export, generated TS client, pagination, idempotency helper | REPO-001 | Health and error formats verified; client generation in CI fails on drift | Contract tests | P1 | DONE (merged via PR #4 to `main` at `85d800d`, 2026-10-24; local acceptance checks recorded in `CLAUDE.md` §12) | DELEGATED |
| TEST-001 | Test harness and generated cross-workspace isolation tests for every tenant table | DB-001 | Test fails if scoping is removed (proves it detects leaks) | The tests themselves | P0 | DONE (verified locally, sabotage proof included; merged via PR #3, 2026-10-24) | DELEGATED |
| SEC-001 | Security baseline: CSRF, cookie flags, security headers, rate limiting, secret scanning, dependency alerts | API-001 | Each control demonstrated by a test or CI check | Negative tests | P0 | IN_REVIEW (implemented on `sec-001-security-baseline`; local checks recorded in `CLAUDE.md` §12; founder review and PR CI pending) | DELEGATED |
| OBS-001 | Structured logging, Sentry, `agent_runs` and cost recording, budget table | API-001 | Errors reach Sentry; a sample task records tokens and cost; logs contain no secrets | Log scan; sample run | P1 | READY | DELEGATED |
| UI-001 | Web app shell, routing, auth screens, API client, state patterns | API-001 | Screens handle loading, empty, error; accessibility checks pass | UI tests | P1 | READY | DELEGATED |

### 7.2 Identity, tenancy, access

| ID | Objective and value | Depends on | Acceptance criteria | Required tests | Pri | Status | Approval |
|---|---|---|---|---|---|---|---|
| AUTH-001 | Signup, login, logout, email verification, Google sign-in, server-side sessions (F-CORE-01) | DB-001, SEC-001 | Flows work; sessions expire and rotate; passwords hashed with Argon2id | Unit, integration, negative cases | P0 | BLOCKED | APPROVED-SCOPE |
| AUTH-002 | Workspaces and server-side tenant scoping (F-CORE-02) | AUTH-001, TEST-001 | Creator becomes owner; switching updates session; every tenant query scoped | Isolation tests | P0 | BLOCKED | APPROVED-SCOPE |
| AUTH-003 | Roles and permission map; `require(permission)` (F-CORE-04, F-SEN-01) | AUTH-002 | Permission matrix enforced on every route | Generated matrix test | P1 | BLOCKED | APPROVED-SCOPE (role list delegated) |

### 7.3 Integrations and agent runtime

| ID | Objective and value | Depends on | Acceptance criteria | Required tests | Pri | Status | Approval |
|---|---|---|---|---|---|---|---|
| INT-001 | Connector framework with encrypted tokens, typed errors, circuit breaker (F-CORE-03) | AUTH-002 | Connect, refresh, revoke; tokens never logged; key rotation works | Integration test; log scan | P1 | BLOCKED | APPROVED-SCOPE |
| INT-003 | `ManualPublish` connector | INT-001 | Post package produced; owner confirms; record stored | Integration test | P1 | BLOCKED | DELEGATED |
| INT-002 | Meta Graph connector for Instagram and Facebook Pages in development mode; **verify** requirements | INT-001, SEN-001 | Publish to a test account after approval; metrics fetch works; findings recorded | Sandbox integration test | P2 | BLOCKED | DELEGATED |
| AI-001 | Agent task runtime: claim, retries, timeouts, step caps, idempotency, reaper for stale tasks (F-CORE-05) | API-001, DB-001 | Retry then visible failure; no duplicate side effect under duplicate delivery or worker crash | Failure-injection tests | P1 | READY | APPROVED-SCOPE |
| AI-002 | LLM client interface, tiers, budgets, structured output with one repair retry; fake provider for tests (labeled) | AI-001, OBS-001 | Invalid output rejected and repaired or failed; provider swappable | Unit tests | P1 | BLOCKED | DELEGATED |
| TEST-002 | AI evaluation harness and first eval sets | AI-002 | Eval runs reproducibly; results stored per prompt version | Harness run | P1 | BLOCKED | DELEGATED |

### 7.4 Modules

| ID | Objective and value | Depends on | Acceptance criteria | Required tests | Pri | Status | Approval |
|---|---|---|---|---|---|---|---|
| CLA-001 | Brand profile capture, versioning, owner approval (F-CLA-01) | AUTH-002, AI-002 | Approved profile is the only one agents use | API and UI tests | P1 | BLOCKED | APPROVED-SCOPE |
| CLA-002 | Brand scoring: deterministic checks plus small-tier rubric (F-CLA-02) | CLA-001, TEST-002 | Eval set of 30+ labeled examples; agreement recorded; threshold chosen from data | Eval run | P1 | BLOCKED | APPROVED-SCOPE |
| MUS-001 | On-brand content generation with scoring and bounded rewrite (F-MUS-01) | CLA-002, AI-001 | Drafts valid JSON; low scores rewritten up to cap, then queued | Eval and failure tests | P1 | BLOCKED | APPROVED-SCOPE |
| SEN-001 | Minimal Sentinel: request, decide, consume, expire, audit; payload-hash binding (subset of F-SEN-02/03) | AUTH-003, DEC-003 | No publish or send without a valid approval; changed payload rejected; one-time use; audit rows written; app role cannot update or delete audit | Approval-bypass tests | P0 | BLOCKED | APPROVED-SCOPE (constraint C-01) |
| MUS-002 | Scheduling and approval-gated publishing (F-MUS-03, F-MUS-04) | MUS-001, SEN-001, INT-003 | Approved item publishes; unapproved cannot | Integration test | P1 | BLOCKED | APPROVED-SCOPE |
| ORB-001 | Goal intake and plan proposal with registry-bounded actions and deterministic validation (F-ORB-01) | CLA-001, AI-001 | Invalid plans rejected; owner approves before execution; models cannot waive approvals | Plan-validity eval; loop and cap tests | P1 | BLOCKED | APPROVED-SCOPE |
| ORB-002 | Initial Orbit dashboard (F-ORB-03) | ORB-001, UI-001 | Shows goals, steps, approvals, results | UI tests | P1 | BLOCKED | APPROVED-SCOPE |
| CON-001 | Lead form endpoint and lead inbox (F-CON-01) | AUTH-002, SEC-001 | Leads arrive tagged by source; spam and rate limits work | Integration and abuse tests | P1 | BLOCKED | APPROVED-SCOPE |
| CON-002 | Contacts, pipeline, deterministic lead scoring v1 (F-CON-02, F-CON-03) | CON-001 | Scores and stages update; events recorded | Unit and API tests | P2 | BLOCKED | APPROVED-SCOPE |

### 7.5 Integration and delivery

| ID | Objective and value | Depends on | Acceptance criteria | Required tests | Pri | Status | Approval |
|---|---|---|---|---|---|---|---|
| E2E-001 | End-to-end MVP loop | all P1 above | Loop completes on staging; approvals enforced | Playwright run (fake LLM, labeled) plus one manual real-provider run | P1 | BLOCKED | DELEGATED |
| DEPLOY-001 | Staging pipeline with manual production promotion; rollback rehearsal | INFRA-001, E2E-001 | Tests gate deploys; rollback tried and documented; backup restore tested once | Rehearsal records | P1 | BLOCKED | DELEGATED |

## 8. Phase 1-S: SEVA 75-day window (only if selected)

| ID | Objective | Depends on | Acceptance criteria | Pri | Status | Approval |
|---|---|---|---|---|---|---|
| SEVA-002 | Map the 75 days onto Phase 1 tasks using `DEVELOPMENT_GUIDE.md` §11; apply cut order | Selection | Schedule recorded; cut order agreed | P1 | BACKLOG | DELEGATED |
| SEVA-003 | Pilot with a few real businesses; record honest results and limits | E2E-001 | Real pilot data and written limitations; demo recorded | P1 | BACKLOG | DELEGATED |

## 9. Phase 2: Market, Pulse basics, Sentinel full, follow-ups, visibility

| ID | Objective | Features | Depends on | Acceptance criteria | Required tests | Pri | Status | Approval |
|---|---|---|---|---|---|---|---|---|
| SEN-002 | Full configurable policies, controlled relaxation for low-risk classes (audited), audit viewer | F-SEN-02/03 | SEN-001 | Relaxations audited; policy changes need owner role; viewer shows complete history | Policy and audit completeness tests | P1 | BACKLOG | APPROVED-SCOPE |
| API-002 | Server-Sent Events for task and approval updates | n/a | API-001 | Live updates replace polling on key screens | Integration tests | P2 | BACKLOG | DELEGATED |
| CON-003 | Conversations and messages; nurture and follow-up agent with approval; email channel | F-CON-04 | SEN-001, INT-001, CON-002 | Drafts in brand voice; opt-out honored; nothing sent without policy-required approval | Consent, opt-out, approval tests | P1 | BACKLOG | APPROVED-SCOPE |
| MKT-001 | Catalog and orders | F-MKT-01 | AUTH-002 | CRUD, order states, tenancy | Unit, integration, isolation | P2 | BACKLOG | APPROVED-SCOPE |
| MKT-002 | Inventory and low-stock signals to Orbit | F-MKT-02 | MKT-001 | Threshold alerts delivered | Unit tests | P2 | BACKLOG | APPROVED-SCOPE |
| MKT-003 | Razorpay payments (test mode first); **verify** compliance and fees | F-MKT-01 | MKT-001, LEGAL-001 | Test-mode orders paid and reconciled; webhooks verified and idempotent | Sandbox tests | P2 | BACKLOG | DELEGATED |
| PUL-001 | Engagement tracking from connectors | F-PUL-01 | INT-002 | Metrics ingested and shown per post | Integration tests | P2 | BACKLOG | APPROVED-SCOPE |
| CLA-003 | AI-visibility tracking via `VisibilityProvider`, repeated runs, rates per platform | F-CLA-03 | RES-001 | Only legal access methods; results show rates with sample sizes | Variation and parser tests | P2 | BLOCKED (RES-001) | APPROVED-SCOPE |
| CLA-004 | Content-fix recommendations | F-CLA-04 | CLA-003 | Prioritized, explained fixes | Eval | P3 | BACKLOG | APPROVED-SCOPE |
| OBS-002 | Alerts: failures, backlog, cost, 5xx, backup | n/a | OBS-001 | Alerts fire in a test | Alert test | P2 | BACKLOG | DELEGATED |

## 10. Phase 3: orchestration, memory, support

| ID | Objective | Features | Depends on | Acceptance criteria | Required tests | Pri | Status | Approval |
|---|---|---|---|---|---|---|---|---|
| ORB-003 | Cross-module goal orchestration across Muse, Convert, Market, Pulse | F-ORB-02 | Phase 2 | Plans meet eval thresholds; budgets and caps hold | Plan evals; loop tests | P2 | BACKLOG | APPROVED-SCOPE |
| ORB-004 | Shared workspace memory with pgvector | F-ORB-06 | DEC-005 | Memory scoped per workspace; improves a measured planning benchmark | Isolation and benchmark tests | P2 | BACKLOG | APPROVED-SCOPE |
| MKT-004 | Customer support agent grounded on store data; refuses when ungrounded | F-MKT-03 | MKT-001, ORB-004 | Groundedness rate meets threshold; ungrounded cases escalate | Groundedness eval; injection tests | P2 | BACKLOG | APPROVED-SCOPE |
| CON-005 | Reply handling: classify, answer simple, escalate | F-CON-05 | CON-003, MKT-004 | Escalation correct on eval set | Eval and injection tests | P2 | BACKLOG | APPROVED-SCOPE |
| MUS-003 | Auto-generated visibility fixes | F-MUS-02 | CLA-004 | Drafts go through approval | Approval tests | P3 | BACKLOG | APPROVED-SCOPE |
| TEST-003 | Expanded eval suites (groundedness, plans, scoring) | n/a | Phase 2 | Thresholds recorded and enforced before prompt or model changes | Eval runs | P2 | BACKLOG | DELEGATED |

## 11. Phase 4: advanced automation

| ID | Objective | Features | Depends on | Acceptance criteria | Pri | Status | Approval |
|---|---|---|---|---|---|---|---|
| PUL-002 | Forecasting baseline (statistical first) | F-PUL-02 | PUL-001 | Forecasts include intervals; backtested | P3 | BACKLOG | APPROVED-SCOPE |
| PUL-003 | Automated A/B experiments with guardrails | F-PUL-03 | PUL-001, SEN-002 | Experiments run only within policy | P3 | BACKLOG | APPROVED-SCOPE |
| PUL-004 | Anomaly alerts with suggested actions | F-PUL-04 | PUL-001 | Alerts evaluated on historical data | P3 | BACKLOG | APPROVED-SCOPE |
| PUL-005 | Competitor and market watch (public sources only) | F-PUL-05 | PUL-001 | Terms-compliant monitoring; summaries feed Clarity and Muse | P3 | BACKLOG | APPROVED-SCOPE |
| ORB-005 | Weekly business summary and ops alerts | F-ORB-04/05 | MKT-002, PUL-001 | Summary accurate against source data | P3 | BACKLOG | APPROVED-SCOPE |
| CON-006 | Call and meeting booking (Google Calendar) | F-CON-06 | CON-003 | Bookings confirmed with owner policy | P3 | BACKLOG | APPROVED-SCOPE |
| CON-007 | Cold-lead re-engagement | F-CON-07 | CON-003 | Opt-out honored; frequency capped | P3 | BACKLOG | APPROVED-SCOPE |
| CON-008 | WhatsApp channel; templates and consent | F-CON-08 | LEGAL-001, CON-003 | Provider rules met | P3 | DEFERRED (consent and cost unvalidated) | DELEGATED |

## 12. Phase 5: beta, hardening, launch

| ID | Objective | Acceptance criteria | Pri | Status | Approval |
|---|---|---|---|---|---|
| SEC-002 | Security review and fixes | Findings triaged; criticals fixed | P1 | BACKLOG | DELEGATED |
| PERF-001 | Load and cost tests | Targets set from data; results recorded | P2 | BACKLOG | DELEGATED |
| BILL-001 | Billing (after pricing evidence) | Test-mode billing works | P2 | BACKLOG | DELEGATED |
| OPS-001 | Runbooks and backup restore drill | Drill recorded | P1 | BACKLOG | DELEGATED |
| BETA-001 | Beta onboarding with consent and data notes | Named pilot users onboarded | P1 | BACKLOG | DELEGATED |
| DEPLOY-002 | Production hardening and go/no-go | Checklist in guide §14 complete | P1 | BACKLOG | DELEGATED |

## 13. Deferred features and reasons

| Item | Reason |
|---|---|
| WhatsApp (`CON-008`) | Consent rules, templates and cost unvalidated |
| AI-visibility (`CLA-003`) until `RES-001` | Legal and reliable access unverified |
| Commission pricing, native mobile apps, Vistaro as merchant of record | Unvalidated; out of first release |
| Embeddings and vector search (`DEC-005`, `ORB-004`) | Not needed for the MVP; chosen when Phase 3 starts |

## 14. Blockers

| Blocker | Affects |
|---|---|
| Repository not yet created | All build tasks |
| Hosting plan, region, `pgvector` availability unverified | `INFRA-001`, Phase 3 |
| Module-name mapping and full report not confirmed | `DOC-001`, naming in code |
| No real owner evidence | `VAL-002`, `SEVA-001`, prioritization |
| AI-platform access unverified | `CLA-003` |
| Meta app review requirements unverified | `INT-002` |

## 15. Next recommended action

1. Review SEC-001 on `sec-001-security-baseline`; keep it `IN_REVIEW` until its checks and review requirements are satisfied.
2. Keep `AUTH-001` blocked until SEC-001 is accepted and marked `DONE`; DB-001 is already complete.
3. `INFRA-001` (staging verification) and the ready non-code tracks can proceed independently.

## 16. Change log

| Date | Change | By |
|---|---|---|
| 2026-10-17 | Initial roadmap | AI-generated |
| 2026-10-18 | Finalized under founders' delegation: stack and architecture decided; DEC-001, DEC-003, DEC-004 done; full task breakdown for phases 1 to 5; approval flags updated | Claude (delegated) |
| 2026-10-23 | `REPO-001`: created the monorepo bootstrap, moved reference docs into `docs/`, added CI and compose files, and verified a fresh clone; task is `IN_REVIEW` pending CI on a PR | Claude (delegated) |
| 2026-10-23 | `REPO-001` merged into `main` via PR #1; CI green on PR #1; task marked `DONE` | Claude (delegated) |
| 2026-10-23 | `DB-001`: roles + `citext` bootstrap via `infra/initdb/`, Alembic base schema with forced RLS on `memberships`; all acceptance checks verified locally on empty and seeded databases; `IN_REVIEW` pending CI on its PR | Claude (delegated) |
| 2026-10-24 | `DB-001` merged into `main` via PR #2; task marked `DONE`; `TEST-001` unblocked | Claude (delegated) |
| 2026-10-24 | `TEST-001`: tenancy harness (`tests/test_tenancy.py`) with fixtures, generated per-table tests, pooled-connection case, and sabotage proof (tests fail when the policy is removed). The harness caught a real defect: after commit the session GUC sits at `''` and the old policy cast errored; migration `0002` fixes the policy with `NULLIF`. CI gained a Postgres service so the harness runs on PRs. `IN_REVIEW` | Claude (delegated) |
| 2026-10-24 | `TEST-001` merged into `main` via PR #3; task marked `DONE`. Next tasks are handed to another teammate | Claude (delegated) |
| 2026-10-24 | `API-001`: error envelope and typed exceptions, request-ID middleware, `/healthz` and `/readyz`, OpenAPI export (`scripts/export_openapi.py`), TypeScript client (`openapi-typescript`), cursor-pagination helper, idempotency-key helper. Contract tests: 47 backend tests (ruff ✅, mypy ✅, lint-imports ✅, pytest 47/47 ✅), 3 frontend tests (lint ✅, typecheck ✅, vitest 3/3 ✅, build ✅). CI drift check added: `export-openapi` job + `codegen:check` in `frontend` job. Negative drift test verified (exit 1 on drift, exit 0 after restore). Branch: `api-001-skeleton`. Status: `IN_REVIEW` — awaiting founder review | Claude (delegated) |
| 2026-10-24 | `API-001` merged to `main` via PR #4 at `85d800d`; SEC-001 dependency satisfied | Claude (delegated) |
| 2026-10-24 | `SEC-001` implemented on `sec-001-security-baseline`: CSRF token endpoint and validation, environment-aware cookie defaults, security headers/CSP/HSTS, Redis fixed-window rate limits, Python/Node dependency audits and Dependabot updates. Status `IN_REVIEW`; checks and limitations in `CLAUDE.md` §12 | Claude (delegated) |
