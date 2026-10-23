# TASK PLAYBOOK — Vistaro

Version 1.0 · 2026-10-18. Step-by-step instructions for **every task** in the roadmap, in execution order, from inspecting the repository to deployment and beyond.

| This file answers | Other files answer |
|---|---|
| **How** to carry out each task, what to verify, what to say to the AI | **What and why, dependencies, acceptance criteria, status:** `/docs/PROJECT_ROADMAP.md` (authoritative). **Current queue:** `/docs/ACTIVE_TASKS.md`. **Design:** `/docs/ARCHITECTURE.md`. **Patterns and conventions:** `/docs/DEVELOPMENT_GUIDE.md`. **Rules:** `/CLAUDE.md` |

**Single source of truth rule:** task *status* lives only in the roadmap. This playbook never records status. If an instruction here conflicts with the roadmap's acceptance criteria, the roadmap wins; fix this file.

**Unverified commands.** Commands below are the *target* commands for the chosen stack. Confirm each against the real repository (package scripts, CI config) before relying on it, then record the working ones in `CLAUDE.md` §12.

---

## 1. Session protocol (use for every task)

### 1.1 Start prompt (copy, replace the ID)

```
Work on <TASK-ID>. Follow CLAUDE.md. First read docs/ACTIVE_TASKS.md, the
roadmap entry for this task, docs/PROJECT_WARNINGS.md (anything touching this
component) and the relevant part of docs/ARCHITECTURE.md. Inspect the real
repository. Then give me a short plan: objective, files you will touch, risks,
tests. Wait for my OK before changing code. Keep the diff small and explain it.
```

### 1.2 After you approve the plan

```
Go ahead. Implement only this task. Do not refactor unrelated code.
```

### 1.3 End prompt

```
Run the relevant checks and show me the real output. Update the roadmap
status only if the acceptance criteria are met and verified. Update
ACTIVE_TASKS.md, add any new warnings, and give me the final report from
CLAUDE.md section 11. List anything you could not verify.
```

### 1.4 Standard checks (targets; confirm in the repo)

| Area | Command (target) |
|---|---|
| Backend lint, types, boundaries | `uv run ruff check .` · `uv run mypy src` · `uv run lint-imports` |
| Backend tests | `uv run pytest -q` |
| Migrations | `uv run alembic upgrade head` then `uv run alembic downgrade -1` then `upgrade head` |
| Frontend | `pnpm lint` · `pnpm typecheck` · `pnpm test` |
| End-to-end | `pnpm test:e2e` (script to be defined in `UI-001` or `E2E-001`) |

### 1.5 Definition of done reminder

A task is `DONE` only when the roadmap acceptance criteria are met **and** the real test output has been seen. Commit after each finished task.

---

## 2. Execution order at a glance

1. **Track A (non-code, start now, in parallel):** `REPO-000`, `DOC-001`, `VAL-001`, `NAME-001`, `RES-001`, `LEGAL-001`, `SEVA-001`; then `VAL-002`.
2. **Wave B, foundation:** `REPO-001`, `INFRA-001`, `DB-001`, `TEST-001`, `API-001`, `SEC-001`, `OBS-001`, `UI-001`.
3. **Wave C, identity:** `AUTH-001`, `AUTH-002`, `AUTH-003`.
4. **Wave D, platform:** `INT-001`, `AI-001`, `AI-002`, `TEST-002`, then confirm `DEC-002`.
5. **Wave E, modules:** `CLA-001`, `CLA-002`, `SEN-001`, `MUS-001`, `INT-003`, `MUS-002`, `ORB-001`, `ORB-002`, `CON-001`, `CON-002`, `INT-002`.
6. **Wave F, delivery:** `E2E-001`, `DEPLOY-001`.
7. **Then** `SEVA-002`/`SEVA-003` (if selected), Phase 2, 3, 4, 5.

Decisions already made (`DEC-001`, `DEC-003`, `DEC-004`) need no work; they are listed in section 3.

---

## 3. Phase 0 tasks: validation, decisions, definition

### REPO-000 — Inspect the repository
**Do**
1. Check whether a repository exists and where. If it does: `git status`, `git branch --show-current`, `git log --oneline -10`, list the tree (excluding dependency folders).
2. Read `README`, package and dependency files, scripts, CI config, Docker files, and any existing `CLAUDE.md` or `AGENTS.md`.
3. Try the install, run, test, lint and build commands you find. Note what works and what fails; do not fix anything yet.
4. Compare what exists with `docs/ARCHITECTURE.md`. List every mismatch.
5. Record the real structure and the commands that actually work in `CLAUDE.md` §12. If no repository exists, record that.

**Verify:** each recorded command was actually run. **Do not** change code, delete, reset or reformat anything.
**Ask the AI:** "Do REPO-000 only. Report findings and mismatches; make no code changes."

### DOC-001 — Reconcile names and the feature report
**Do (founders)**
1. Share the full *Product Features & Functional Responsibilities Report*.
2. For each pair, confirm or correct: Lens→Clarity, Dream→Muse, Lead Master→Convert, Store Manager→Market, Engagement Tracking→Pulse; Sentinel new.
3. Have the AI diff the report against both master documents and list differences. Decide each difference.
4. Update the master documents and `docs/PROJECT_WARNINGS.md` (WARN-G-001, WARN-G-005).

**Verify:** the founders confirmed in writing; no module name differs between documents.

### VAL-001 — Interview real business owners
**Do (founders)**
1. Decide the number of interviews first (a suggestion is 10 to 15 across at least two business types; your call).
2. Find owners: local shops, home-based sellers, Instagram sellers, campus entrepreneurs, E-Cell contacts.
3. Use a fixed script. Core questions: hours per week on marketing and replies; where enquiries arrive and how fast they are answered; what percentage get no reply within a day; which tools they use; do they know if AI assistants mention their business; would they let software post or message for them with approval; what they pay for tools today.
4. Record exact quotes and numbers. Keep interviewees' consent and anonymity notes. Store notes in a shared folder.
5. Rank pains from evidence, not impressions.

**Verify:** the planned count was met; every claim you later make cites an interview or survey.

### VAL-002 — Choose the first niche
**Do:** after `VAL-001`, compare niches on pain intensity, reachability, willingness to pay, channel fit (Instagram, WhatsApp), and your access. Pick one. Record it in the decision log (`STARTUP_AI_MASTER_CONTEXT.md` §2.6) and resolve OQ-03.
**Verify:** founders signed off.

### NAME-001 — Check the name
**Do:** search the web with "Vistaro" plus "ai", "marketing", "app"; check domains (.com, .ai, .in) and handles (Instagram, X, LinkedIn, YouTube); check the IP India trademark database for classes 9, 35, 42; check Play Store and App Store. Record dated results.
**Verify:** results recorded; founders decide go or no-go. If there is a conflict, do not spend on branding until resolved.

### RES-001 — AI-platform access research
**Do:** for ChatGPT, Gemini, Perplexity, Google AI Overviews: find whether an official programmatic way exists to obtain answers; what its terms allow; whether API answers match consumer-app answers; pricing and rate limits. Cite sources and dates. Conclude per platform: supported, partially supported, or unsupported.
**Verify:** each conclusion has a source. **Do not** recommend scraping that violates terms. Update WARN-C-001.

### LEGAL-001 — Legal advice
**Do:** ask a qualified advisor: data protection obligations for customer data (consent, retention, deletion, cross-border processing by LLM providers); messaging consent and opt-out rules (email, WhatsApp); terms for publishing on behalf of customers; what a pilot consent note should say. Record answers in `docs/PROJECT_WARNINGS.md`.
**Verify:** advisor input written down. This is not legal advice from the AI.

### DEC-001 — Stack and hosting (decided)
Done. See `docs/ARCHITECTURE.md` ADR-001 to ADR-020. No action unless you want to change it (`CLAUDE.md` §9).

### DEC-002 — Confirm LLM provider and model tiers
**Do (after `AI-002`, `TEST-002`):** run candidate models on a fixed task set: brand scoring against your labeled examples, content generation quality, plan validity, structured-output failure rate, latency, cost per task. Pick the model for each tier; set `LLM_MODEL_LARGE` and `LLM_MODEL_SMALL`. Record results.
**Verify:** evaluation actually run; results stored.

### DEC-003 and DEC-004 — Decided
Done: minimal approval step in Phase 1; competitor watch lives in Pulse. No action.

### DEC-005 — Embeddings provider (Phase 3)
**Do (at Phase 3 start):** compare candidates on Hindi and English retrieval quality, cost, and data handling using a small labeled retrieval set. Choose and record.
**Verify:** evaluation run.

### SEVA-001 — Finish the SEVA Stage 1 submission
**Do**
1. Get the deadline and the official template. Fill every required point (1, 2, 6, 7, 9, 10, 11 and the PPT).
2. Use only real evidence from `VAL-001`; label assumptions as assumptions.
3. Use canonical module names and the two-person team (WARN-G-002). Replace the illustrative "challenges" text (WARN-G-003).
4. Keep the PPT under 20 MB; save a draft first, then submit.

**Verify:** checked against the rubric; every number has a source.

---

## 4. Phase 1 tasks: core platform and MVP loop

For each task: use the start prompt in §1.1; do the steps; run checks in §1.4; end with §1.3.

### REPO-001 — Create the repository
**Do:** follow `DEVELOPMENT_GUIDE.md` §2: layout, `.gitignore`, `.editorconfig`, `.env.example` (names only), `README` with verified commands, `infra/docker-compose.yml`, CI workflow (lint, types, tests, import-linter, secret scan). Copy in `CLAUDE.md`, `AGENTS.md`, `docs/`, the two master documents.
**Verify:** fresh clone in a new folder installs and runs both apps using only the README; CI runs on a test pull request; secret scan clean.
**Watch for:** committing `.env`; unpinned dependencies (use lockfiles).

### INFRA-001 — Local services and staging
**Do:** finalize docker-compose (Postgres, Redis, Mailpit); create staging on Render and Cloudflare Pages; set secrets in the platform store; **verify** plan, region, credits, `pgvector` availability, and record findings (WARN-F-007).
**Verify:** staging URL reachable; `/healthz` responds; no secrets in the repository.
**Watch for:** using production-like secrets locally; skipping the spending limit on the LLM key.

### DB-001 — Roles, extensions, base schema
**Do:** create roles `vistaro_migrator` (owner) and `vistaro_app` (no `BYPASSRLS`); enable `citext`; write Alembic migrations for `users`, `workspaces`, `memberships`, `sessions`; enable and force RLS on tenant tables; document the `sessions` exception (WARN-D-007).
**Verify:** `alembic upgrade head`, `downgrade -1`, `upgrade head` all succeed on empty and seeded databases; connecting as `vistaro_app` cannot bypass RLS.
**Watch for:** running the app as the table owner (RLS then does nothing).

### TEST-001 — Tenancy test harness
**Do:** build the test fixtures (two workspaces, rows for each); write a generated test per tenant table: as workspace A with application filters removed, assert zero rows from B; include a pooled-connection reuse case (WARN-B-009).
**Verify:** deliberately remove the policy on one table and confirm the test fails, then restore it.
**Rule:** every new tenant table must get this test.

### API-001 — API skeleton
**Do:** error envelope and typed exceptions, request-ID middleware, `/healthz` and `/readyz`, OpenAPI export, generated TypeScript client, cursor pagination helper, idempotency-key helper.
**Verify:** contract tests; client generation in CI fails on a deliberately introduced drift.

### SEC-001 — Security baseline
**Do:** CSRF protection, cookie flags (HttpOnly, Secure, SameSite), security headers and CSP, Redis-backed rate limiting, secret scanning and dependency alerts in CI.
**Verify:** negative tests: missing CSRF token rejected, rate limit triggers, headers present. **Watch for:** relaxing CORS to `*`.

### OBS-001 — Observability and cost recording
**Do:** structlog with request, workspace and task IDs; Sentry in API and worker; `agent_runs` and `workspace_budgets` tables with a recording helper; redaction filter.
**Verify:** a forced error reaches Sentry; a sample task writes tokens and cost; log scan finds no secrets or message bodies.

### UI-001 — Web app shell
**Do:** routing, layout, auth screens (visual only until `AUTH-001`), API client with credentials and CSRF header, query patterns, loading/empty/error components, accessibility basics, the Playwright setup and `test:e2e` script.
**Verify:** component tests; automated accessibility check; keyboard navigation checked manually.

### AUTH-001 — Authentication
**Do:** signup, login, logout, email verification (Resend), Google sign-in (Authlib), server-side sessions with rotation and expiry, Argon2id hashing.
**Verify:** tests for success and failure paths (wrong password, expired token, reused verification link, session fixation attempt); manual check of cookie flags.
**Watch for:** logging passwords or tokens; leaking whether an email is registered.

### AUTH-002 — Workspaces and tenant scoping
**Do:** workspace creation (creator is owner), switching, invitation of members; the `tenant_session` helper; apply to every repository.
**Verify:** `TEST-001` passes for all tenant tables; a route given another workspace's ID returns not found or forbidden.

### AUTH-003 — Roles and permissions
**Do:** single role-to-permission map; `require(permission)` dependency; approver rules (requester cannot approve their own agent request without an approver role).
**Verify:** generated matrix test covering every role on every protected route.

### INT-001 — Connector framework
**Do:** connector interface (`connect`, `refresh`, `revoke`, `publish`, `fetch_metrics`), typed errors, circuit breaker, AES-GCM or Fernet token encryption with `key_id`, key-rotation job.
**Verify:** connect, refresh and revoke against a fake connector (labeled); log scan shows no tokens; rotate a key and read old tokens.

### AI-001 — Agent task runtime
**Do:** Celery app; atomic task claim; retries with backoff for transient errors; timeouts; step cap; idempotency; reaper for stale `running` tasks; agent action registry (whitelist, with `requires_approval` set in the registry).
**Verify:** failure-injection tests: duplicate delivery, worker crash mid-step, transient then success, permanent failure; assert no duplicate side effect.

### AI-002 — LLM client and structured output
**Do:** `LLMClient` interface, tiers, budget check before each call, `agent_runs` recording, structured-output helper with one repair retry, fake provider for tests (clearly labeled).
**Verify:** tests for invalid JSON, schema violation, repair success, repair failure, budget exceeded. One manual call with the real provider using a spending-limited key.

### TEST-002 — AI evaluation harness
**Do:** `tests/evals/` with dataset loader, runner, and stored results per prompt version. Create the first eval sets: 30+ labeled brand examples (good, off-brand, borderline) written by the founders; plan-validity cases.
**Verify:** the same eval run twice gives comparable results; results saved.

### CLA-001 — Brand profile
**Do:** versioned `brand_profiles`; guided interview form (tone words, audience, banned terms, required elements, 3 to 5 sample posts); owner approval; agents may only use an approved profile.
**Verify:** API and UI tests; an unapproved profile cannot be used by generation.

### CLA-002 — Brand scoring
**Do:** deterministic checks (banned terms, length, required elements, language) then small-tier LLM rubric; combine into a 0 to 100 score with explanation; tune the pass threshold (initial 70) from the eval set.
**Verify:** record agreement with the founders' labels; document the chosen threshold and why.

### SEN-001 — Minimal Sentinel
**Do:** policies (default: approval required), `request_approval`, decisions, `consume` with payload-hash binding and one-time use, expiry, audit writes; app role has INSERT and SELECT only on `audit_logs`; approvals inbox endpoints.
**Verify:** bypass tests: publish without approval fails; changed payload fails; reuse fails; expired fails; audit rows exist; app role cannot update or delete audit rows.
**Priority:** `P0`. Nothing may publish or send before this passes.

### MUS-001 — Content generation
**Do:** generation action using the approved brand profile, goal and channel; validated JSON output; score; rewrite up to two times if below threshold; then queue for approval.
**Verify:** eval on a fixed prompt set; failure tests (invalid output, scoring failure); generated content never published without approval.

### INT-003 — ManualPublish connector
**Do:** produce the final post package (text, hashtags, alt text, scheduled time); owner confirms they published; record the confirmation and optional post URL.
**Verify:** integration test of the full manual flow.

### MUS-002 — Scheduling and publishing
**Do:** schedule approved content; at publish time call `consume(approval_id, payload)` immediately before the connector call; record external ID before acknowledging success; handle failures visibly.
**Verify:** approved item publishes once even under duplicate delivery; unapproved item cannot publish.

### ORB-001 — Goals and plans
**Do:** goal intake; planner prompt that receives the **registry of allowed actions**; deterministic plan validation (schema, whitelist, acyclic, step cap, registry-set approvals, budget); plan review and approval; create `tasks` rows; dispatcher.
**Verify:** plan-validity eval; tests that a plan with an unknown action, a cycle, or a skipped approval is rejected; loop and step-cap tests.

### ORB-002 — Orbit dashboard
**Do:** goal and step status, pending approvals, results, errors with retry or "ask me"; polling every few seconds.
**Verify:** UI tests for loading, empty, error, success; manual walkthrough of the core loop screens.

### CON-001 — Lead form and inbox
**Do:** public form endpoint with token, rate limit, honeypot, validation; create contact, lead, and `lead_events`; lead inbox UI.
**Verify:** abuse tests (spam, oversized input, duplicate submit); tenancy test for the new tables.

### CON-002 — Pipeline and lead scoring v1
**Do:** stage changes with events; deterministic scoring (source, form completeness, replied, recency, interest keywords); hot, warm, cold labels.
**Verify:** unit tests for scoring rules; weights documented as initial defaults.

### INT-002 — Meta Graph connector (development mode)
**Do:** **verify** current requirements first (business account, app roles, permissions, review) and record them; implement OAuth, publish to a test Instagram or Facebook Page after approval, fetch basic metrics.
**Verify:** sandbox publish with an approved item; token handling log scan. If requirements block you, keep `ManualPublish` and record the blocker (WARN-C-005).

### E2E-001 — End-to-end loop
**Do:** Playwright test of the full MVP loop with the fake LLM provider (labeled); one manual run with the real provider and `ManualPublish`.
**Verify:** loop completes on staging; approvals enforced; tenancy and bypass tests green in CI.

### DEPLOY-001 — Staging pipeline and rehearsal
**Do:** CI gates deploys; staging auto-deploys on merge; production needs manual approval; rehearse a rollback; take and restore a backup once.
**Verify:** records of the rollback rehearsal and the restore. This completes the MVP.

---
## 5. Phase 1-S: SEVA window (only if selected)

### SEVA-002 — Map the 75 days
**Do:** use `DEVELOPMENT_GUIDE.md` §11; assign tasks to Anushka (frontend and platform) and Dimple (AI and backend); agree the cut order (live Meta connector first, then scoring polish, then dashboard extras; never cut approvals, tenancy tests, or audit).
**Verify:** schedule written and agreed.

### SEVA-003 — Pilot and honest report
**Do:** onboard a few real businesses with a written consent and data-handling note; run the loop; log time saved, lead counts, approval edits, failures; write the demo and report stating what is real, test-account, or mocked.
**Verify:** every number in the report comes from the pilot log.

---

## 6. Phase 2 tasks: Market, Pulse basics, Sentinel full, follow-ups, visibility

Start Phase 2 only after the MVP acceptance in the roadmap §4 is met.

### SEN-002 — Full policies and audit viewer
**Do:** configurable policy per action type; controlled relaxation for low-risk classes (for example replies from approved templates) that is itself audited and owner-only; audit viewer with filters.
**Verify:** policy and audit-completeness tests; relaxation cannot apply to publish or financial actions unless explicitly designed and approved by the founders.

### API-002 — Server-Sent Events
**Do:** SSE endpoint for task and approval updates, tenant-scoped; replace polling on key screens; keep polling as fallback.
**Verify:** integration test of scoped streams; no cross-workspace events.

### CON-003 — Conversations and follow-up agent
**Do:** `conversations` and `messages` tables with RLS; email channel; nurture agent drafts follow-ups in brand voice; sends only through `SEN` approval policy; honor `opted_out_at`; frequency caps.
**Verify:** consent and opt-out tests; approval-bypass test for sends; tenancy test; eval on draft quality. Apply `LEGAL-001` findings first.

### MKT-001 — Catalog and orders
**Do:** `products`, `orders`, `order_items` with RLS; CRUD and order states; link orders to leads through `convert`'s service.
**Verify:** unit and integration tests; tenancy test; module-boundary check (no direct table access across modules).

### MKT-002 — Inventory and low-stock signals
**Do:** `inventory` with thresholds; deterministic alerts to Orbit; no AI for arithmetic.
**Verify:** unit tests for thresholds and edge cases (zero, negative adjustments).

### MKT-003 — Razorpay payments
**Do:** **verify** onboarding, compliance, and fees; implement in test mode; signed webhooks with idempotent handling; reconciliation job; no card data stored.
**Verify:** sandbox payment, refund, duplicate webhook tests; `LEGAL-001` input recorded. **Ask founders before any live-mode switch.**

### PUL-001 — Engagement tracking
**Do:** ingest metrics from connectors on a schedule; store per post; simple views; handle API limits.
**Verify:** integration tests with sandbox data; rate-limit handling test.

### CLA-003 — AI-visibility tracking
**Do:** only after `RES-001`; implement `VisibilityProvider` for platforms marked supported; repeat each query several times (default 5, tunable); store results; report mention rates with sample sizes; cache within a window.
**Verify:** variation test; parser accuracy on a labeled sample; no scraping that violates terms; unsupported platforms shown as "not measurable", never faked.

### CLA-004 — Content-fix recommendations
**Do:** analyze visibility gaps; produce prioritized, explained fixes; no auto-publishing.
**Verify:** eval with founders' judgment on usefulness.

### OBS-002 — Alerts
**Do:** alerts for failure spikes, queue backlog, cost threshold, 5xx rate, backup failure.
**Verify:** trigger each alert in staging.

---

## 7. Phase 3 tasks: orchestration, memory, support

### ORB-003 — Cross-module orchestration
**Do:** extend the registry with Convert, Market, Pulse actions; plan across modules; keep step caps and budgets; conflict handling (for example two plans scheduling the same slot).
**Verify:** plan-validity evals on multi-module goals; loop and cap tests; cost per goal recorded.

### ORB-004 — Shared memory
**Do:** after `DEC-005`; enable `pgvector` (verify host support); `memory_items` with RLS; store outcomes, preferences and decisions; retrieval scoped by workspace; owner can view and delete memories.
**Verify:** isolation tests including vector queries; benchmark showing the planner improves with memory; deletion works.

### MKT-004 — Support agent
**Do:** retrieval over the workspace's product, order and FAQ data; answer only from retrieved data; refuse and escalate when ungrounded; treat customer text as untrusted; restricted tools.
**Verify:** groundedness eval; prompt-injection test set; escalation tests.

### CON-005 — Reply handling
**Do:** classify inbound messages; answer simple questions via the support agent; escalate others; log everything.
**Verify:** escalation accuracy on a labeled set; injection tests; approval policy respected.

### MUS-003 — Auto-generated visibility fixes
**Do:** draft content from `CLA-004` output; always through approval.
**Verify:** approval tests; brand scoring applied.

### TEST-003 — Expanded evals
**Do:** add groundedness, planning, scoring, and reply-handling eval suites with recorded thresholds; make evals a required step before prompt or model changes.
**Verify:** thresholds documented; a deliberately degraded prompt fails the eval.

---

## 8. Phase 4 tasks: advanced automation

### PUL-002 — Forecasting baseline
**Do:** start with simple statistical baselines; backtest on historical data; show intervals, not single numbers.
**Verify:** backtest results recorded; never presented as guarantees.

### PUL-003 — Automated experiments
**Do:** A/B tests on hooks and timing with guardrails (sample size, duration, approval for anything public, kill switch).
**Verify:** statistical sanity checks; policy tests; audit entries for every experiment action.

### PUL-004 — Anomaly alerts
**Do:** detect deviations on metrics; attach a suggested action; avoid alert fatigue (thresholds, deduplication).
**Verify:** evaluate on historical data; false-positive rate recorded.

### PUL-005 — Competitor and market watch
**Do:** public sources only; respect terms and robots rules; summarize changes; feed Clarity and Muse through their services.
**Verify:** terms review recorded; summaries traceable to sources.

### ORB-005 — Weekly summary and ops alerts
**Do:** deterministic aggregation of leads, orders, engagement, stock; AI writes the narrative only; reorder and payment reminders by rules.
**Verify:** every number in a summary matches source data in a test.

### CON-006 — Booking
**Do:** Google Calendar OAuth with minimal scopes; propose slots; confirm under policy.
**Verify:** integration tests with a test calendar; time-zone tests.

### CON-007 — Re-engagement
**Do:** inactivity triggers; frequency caps; honor opt-out; approval policy.
**Verify:** opt-out and cap tests.

### CON-008 — WhatsApp (deferred)
**Do:** only after `LEGAL-001` and a decision to proceed; implement templates, consent capture and provider rules.
**Verify:** consent flow tests; provider policy review recorded. **Ask founders first.**

---

## 9. Phase 5 tasks: beta, hardening, launch

### SEC-002 — Security review
**Do:** independent review of auth, sessions, tenancy, approvals, connectors, uploads; fix criticals and highs; retest.
**Verify:** findings log with status.

### PERF-001 — Load and cost tests
**Do:** load the API and the queue; measure cost per goal and per workspace; set targets from data.
**Verify:** results recorded; limits and budgets adjusted.

### BILL-001 — Billing
**Do:** only after pricing evidence; test mode first; usage metering from `agent_runs`.
**Verify:** test-mode invoices reconcile with usage.

### OPS-001 — Runbooks and drills
**Do:** write runbooks (incident, rollback, secret rotation, restore); run a restore drill and a rollback drill.
**Verify:** drill records.

### BETA-001 — Beta onboarding
**Do:** named pilot users; consent and data-handling notes; deletion path; feedback loop.
**Verify:** each pilot user has consent on file.

### DEPLOY-002 — Production hardening and go/no-go
**Do:** complete the "ready to pilot" list in `DEVELOPMENT_GUIDE.md` §14; confirm monitoring, backups, alerts; founders make a recorded go or no-go.
**Verify:** checklist complete; decision recorded.

---

## 10. After every task (checklist)

1. Checks run, real output seen; failures explained.
2. Roadmap status updated **only** if acceptance criteria are met and verified.
3. `ACTIVE_TASKS.md` updated: current task moved on, next tasks promoted.
4. `docs/PROJECT_WARNINGS.md` updated for new or resolved risks.
5. Architecture, API, schema or setup docs updated if they changed.
6. Commit with the task ID in the message.
7. Final report received in the `CLAUDE.md` §11 format.

## 11. When something goes wrong

| Situation | Action |
|---|---|
| A check fails and you cannot fix it in the task | Record it in the warnings register; set the task `BLOCKED` with the reason; do not mark it `DONE` |
| The docs disagree with the code | Report the mismatch; propose a fix; do not guess (`CLAUDE.md` §6) |
| A task needs an architecture change | Stop; use the `CLAUDE.md` §9 proposal process |
| A destructive or production-affecting step is needed | Stop and ask the founders |
| The plan is too big for one session | Split the task into smaller tasks with new IDs flagged `PROPOSED-TASK` and ask the founders to accept them |
