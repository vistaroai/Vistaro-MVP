# PROJECT ROADMAP — Vistaro

Living implementation roadmap. Last updated: 2026-10-22 (stack finalized as free and open source only).
Rules and workflow: `/CLAUDE.md`. Architecture and stack (authority): `/docs/ARCHITECTURE.md` v1.1. Current queue: `/docs/ACTIVE_TASKS.md`. Risks: `/docs/PROJECT_WARNINGS.md`.
Product context: `STARTUP_AI_MASTER_CONTEXT.md` (feature IDs `F-*`, decisions `D-*`, open questions `OQ-*`).

---

## 1. Current project stage

| Item | State |
|---|---|
| Stage | Idea and validation. Competition: DTU SEVA 2026, Stage 1 (Screen-1 ideation). |
| Repository | **UNVERIFIED.** None was visible when this roadmap was created. |
| Implemented features | **None verified.** |
| Stack and hosting | **Decided** (`ARCHITECTURE.md` v1.1, `DEC-001`): free and open source only; self-hosted Docker Compose on a free VM; self-hosted open-weight LLM. |
| LLM model, VM provider and domain, backup destination, pricing, first niche | **Undecided** (`DEC-002`, `DEC-005`, `DEC-006`, OQ-09, `VAL-002`). |
| Team | 2 people: Anushka Varshney (frontend and platform), Dimple (AI and backend). |

**Truthfulness rule:** every task below starts at `BACKLOG`, `READY` or `BLOCKED`. Nothing is `DONE`. When you inspect a repository and find code, mark it `IN_REVIEW` until acceptance criteria are verified (see `CLAUDE.md` §12).

### Status summary (the seven required categories)

| Category | Items |
|---|---|
| 1. Completed and verified | None in code. Decision `DEC-001` (stack) is recorded as `DONE` (decision task, not a feature) |
| 2. Implemented but not fully verified | None known. Check the repository (`REPO-000`). |
| 3. In progress | None recorded. |
| 4. Ready to implement | `REPO-000`, `VAL-001`, `NAME-001`, `DOC-001`, `RES-001`, `LEGAL-001`, `SEVA-001`, `DEC-002`, `DEC-003`, `DEC-005`, `DEC-006` (all non-code; see section 5) |
| 5. Blocked | `VAL-002` (needs `VAL-001`); `REPO-001` (needs `REPO-000`); all other build tasks blocked by `REPO-001`; `INFRA-001` also by `DEC-005`; `SEN-001` also by `DEC-003` |
| 6. Planned for later | Phases 2, 3, 4 (section 7) |
| 7. Undecided | LLM model, VM provider and domain, backup destination, niche, tagline, pricing, competitor-watch placement, minimal approval in Phase 1 (section 8) |

---

## 2. Definitions

**Statuses:** `BACKLOG` (not yet actionable), `READY` (can start now), `IN_PROGRESS`, `BLOCKED` (named dependency or decision missing), `IN_REVIEW` (implemented, verification pending), `DONE` (acceptance criteria met and verification recorded), `DEFERRED` (intentionally postponed, reason recorded).

**Priorities:** `P0` blocks everything or is a safety requirement; `P1` required for the MVP loop; `P2` important after the MVP loop; `P3` later or optional.

**Approval flag:**
- `APPROVED-SCOPE`: the capability is in the founders' confirmed spec (product set, four-phase plan, approval constraints).
- `PROPOSED-TASK`: the task breakdown was drafted by an AI and is **not** approved. Treat as a suggestion until the founders accept it.

**Relevant files/components:** unknown until a repository is inspected. When starting a task, add the verified paths under the task in the table notes or a linked task note.

**Task ID prefixes:** `VAL` validation, `NAME` naming, `DOC` documentation, `RES` research, `LEGAL` legal, `DEC` decision, `SEVA` competition, `REPO` repository, `INFRA` infrastructure, `DB` database, `AUTH` auth and tenancy, `API` API, `INT` integrations, `AI` agent runtime, `CLA` Clarity, `MUS` Muse, `CON` Convert, `MKT` Market, `SEN` Sentinel, `PUL` Pulse, `ORB` Orbit, `UI` frontend, `TEST` testing, `DEPLOY` deployment.

---

## 3. MVP definition

**Proposed MVP (`PROPOSED-TASK`; scope from the confirmed Phase 1):** one complete loop:

> Owner states a goal → Orbit proposes a plan → owner approves → Muse drafts on-brand content → Clarity scores it → owner approves via Sentinel → content publishes → Convert captures a lead and drafts a follow-up → Orbit reports progress.

Included: core platform; basic Orbit dashboard and goal flow; Clarity brand profile and scoring; Muse generation and publishing; Convert inbox, scoring and pipeline; **a minimal approval step**.
Excluded from MVP: Market (store), Pulse (experiments, forecasting, competitor watch), AI-visibility tracking, shared memory, advanced automation, WhatsApp, call booking.

**MVP acceptance (binary):** the loop completes in staging with real data; approvals are enforced for every public or outbound action; tests show no cross-workspace data access.

---

## 4. Phases and order of implementation

| Phase | Name | Source | Status |
|---|---|---|---|
| 0 | Validation and definition | Proposed | `READY` (not started) |
| 1 | Core platform: auth, workspaces, integrations framework, basic RBAC, agent task runtime, initial Orbit dashboard, initial Clarity, Muse, Convert | Confirmed spec | `BLOCKED` by `REPO-000` and `REPO-001` (stack is decided) |
| 1-S | SEVA prototype slice (75 days, only if selected) | Proposed | `BACKLOG` |
| 2 | Market, Pulse, Sentinel approvals and audit | Confirmed spec | `BACKLOG` |
| 3 | Goal-driven orchestration and shared memory | Confirmed spec | `BACKLOG` |
| 4 | Advanced automation | Confirmed spec | `BACKLOG` |
| 5 | Beta, hardening, launch | Proposed | `BACKLOG` |

**Dependency chain (critical path):** `REPO-000` → `REPO-001` → `DB-001` → `AUTH-001/002` → `AI-001/002` → `CLA-001` → `MUS-001` and `SEN-001` → `ORB-001` → `CON-001` → `E2E-001`.
**Parallel tracks:** `INFRA-002` (self-hosted LLM and capacity test) feeds `AI-002` and `DEC-002`; `DEC-005` → `INFRA-001` → `DEPLOY-001`; `INFRA-003` (backups) must exist before any production data.

---

## 5. Phase 0 tasks: validation and definition

None of these writes product code. Status `READY` means a person or agent can start now.

| ID | Objective and value | Depends on | Acceptance criteria | Required tests / verification | Pri | Status | Approval | Risks / blockers |
|---|---|---|---|---|---|---|---|---|
| REPO-000 | Locate and inspect the actual repository (if any); record real structure and commands in `CLAUDE.md` §12. Value: stops the docs from drifting from reality. | none | Repo location, branch, tree and verified commands recorded, or "no repository exists" recorded | Commands actually run and output noted | P0 | READY | PROPOSED-TASK | None |
| DOC-001 | Reconcile module names and obtain the full *Product Features & Functional Responsibilities Report*; confirm the Lens-to-Clarity style mapping (OQ-02). Value: one vocabulary in docs and code. | founders sharing the report | Mapping confirmed in writing; master docs updated for any differences | Diff of report vs master docs reviewed by founders | P0 | READY | PROPOSED-TASK | Report text not seen by the authors of the master docs |
| VAL-001 | Interview real business owners with a written script; capture verbatim quotes and numbers. Value: evidence for the product and for SEVA. | none | Interview count set by founders in advance and met; notes stored; top pains ranked from evidence | Coverage checked against the script | P0 | READY | PROPOSED-TASK | Hard-to-reach owners; biased sample |
| VAL-002 | Choose the first niche (OQ-03). | VAL-001 | Niche chosen and recorded in the decision log | Founders sign off | P0 | BLOCKED (VAL-001) | PROPOSED-TASK | None |
| NAME-001 | Check the name "Vistaro": web search, domains, handles, trademark classes 9, 35 and 42, app stores (OQ-01). | none | Results recorded with dates; go/no-go by founders | Searches actually run | P1 | READY | PROPOSED-TASK | Possible conflict |
| RES-001 | Research how AI-platform answers can be obtained legally and reliably (OQ-05). Value: decides whether AI-visibility features are feasible. | none | Per-platform access method and terms summarized with sources and dates | Sources cited | P1 | READY | PROPOSED-TASK | Access may be restricted |
| LEGAL-001 | Get qualified advice on data protection and messaging consent (OQ-12). | none | Written constraints recorded in warnings register | Advisor input recorded | P1 | READY | PROPOSED-TASK | Cost of advice |
| DEC-001 | Decide the technology stack and hosting (OQ-08). | DOC-001 | Decision recorded with rationale; `CLAUDE.md` §9 updated | Founders sign off | P0 | **DONE** 2026-10-22: `ARCHITECTURE.md` v1.1, free and open source only; `CLAUDE.md` §9 updated; signed off by Dimple. Anushka Varshney's acknowledgment pending (either founder may veto) | PROPOSED-TASK | Master documents (not seen) may still show the old suggestion (WARN-G-007) |
| DEC-002 | Evaluate and choose the self-hosted open-weight model(s) and quantization (OQ-10). | DEC-001, INFRA-002 | Candidates with permissive licences compared on a fixed task set (structured output validity, brand-voice quality, latency on the target VM); licence file of the winner recorded | Evaluation actually run; licence checked | P1 | READY | PROPOSED-TASK | Small models on a CPU-only VM may be too slow or weak (WARN-C-009, WARN-F-007) |
| DEC-005 | Choose the VM provider, region and domain name (needed for HTTPS, Google sign-in, email SPF/DKIM). Default candidate: Oracle Cloud Always Free; verify allowance, idle-reclamation rules and terms. | none | Decision recorded with the verified free allowance and its source and date | Provider terms read and cited | P0 | READY | PROPOSED-TASK | Free tier may be unavailable or reclaimed (WARN-F-008) |
| DEC-006 | Choose an off-VM backup destination. | none | Destination recorded; it is not the same VM or disk | Founders sign off | P0 | READY | PROPOSED-TASK | No free second location available |
| DEC-003 | Decide whether a minimal approval step ships in Phase 1 (OQ-07). Recommended: yes, because approvals are mandatory for public actions. | none | Decision recorded | Founders sign off | P0 | READY | PROPOSED-TASK | Scope |
| DEC-004 | Decide where competitor monitoring lives, Pulse or Clarity (OQ-06). | none | Decision recorded | Founders sign off | P3 | READY | PROPOSED-TASK | None |
| SEVA-001 | Complete the SEVA Stage 1 deck and 12-point dossier using only real evidence and the two-person team. | VAL-001 (for evidence), DOC-001 | Deck on the official template, under 20 MB; every required point filled; assumptions labeled | Checked against the SEVA rubric and rules | P0 (deadline unknown) | READY | PROPOSED-TASK | Deadline not known; evidence gap |

---

## 6. Phase 1 tasks: core platform (scope approved; breakdown proposed)

All depend on `DEC-001` (stack) unless noted. Components and files are unknown until the repository exists.

### Foundation

| ID | Objective and value | Depends on | Acceptance criteria | Required tests | Pri | Status | Approval |
|---|---|---|---|---|---|---|---|
| REPO-001 | Create the monorepo per `ARCHITECTURE.md` §3, branching rules, `.env.example`, README with real commands; CI running lint, types, tests, import-linter, secret scan and the **licence check** (ADR-021) | REPO-000 | Repo exists; install and run commands documented and verified; CI gates run and fail when a disallowed licence or a forbidden import is added | Fresh-clone install and run test; deliberate licence and import violations are caught | P0 | BLOCKED (REPO-000) | PROPOSED-TASK |
| INFRA-001 | Self-hosted environments: Docker Compose (dev, staging, production), Caddy with HTTPS, internal-only networking, SOPS + age secrets, host hardening; verify Celery works with Valkey and that all images have arm64 builds | REPO-001, DEC-005 | Staging reachable over HTTPS; only ports 80, 443 and SSH open; no secrets in repo (scan); Valkey/Celery smoke test passes | Secret scan; port scan from outside; environment smoke test | P0 | BLOCKED | PROPOSED-TASK |
| INFRA-002 | Self-hosted LLM server (Ollama or llama.cpp server) in the Compose stack, internal-only; measure latency, parallelism and JSON-schema output on the target VM and on a developer laptop | REPO-001 | Report of measured latency and concurrency per candidate model; server unreachable from the internet | Measurements actually run; external reachability test | P1 | BLOCKED | PROPOSED-TASK |
| INFRA-003 | Backups: nightly `pg_dump` plus restic to the off-VM destination, monthly restore test, backup-before-migration script | REPO-001, DEC-006 | A backup restores into a clean database and the data matches | Restore test recorded | P0 | BLOCKED | PROPOSED-TASK |
| INFRA-004 | Observability: GlitchTip (own database), Uptime Kuma, log rotation, alerts for failures, disk, certificates and backups | INFRA-001 | A forced error and a forced outage each raise an alert | Alert test | P1 | BLOCKED | PROPOSED-TASK |
| DB-001 | Base schema and migrations: users, workspaces, memberships | REPO-001 | Migrations apply and roll back cleanly | Migration up/down test on empty and seeded DB | P0 | BLOCKED | PROPOSED-TASK |
| API-001 | API skeleton: versioning, error envelope, validation, health endpoint | REPO-001 | Health endpoint and error format verified | Contract tests | P1 | BLOCKED | PROPOSED-TASK |
| TEST-001 | Test harness including cross-workspace isolation tests | REPO-001 | Isolation test fails when scoping is removed (proves it works) | The tests themselves | P0 | BLOCKED | PROPOSED-TASK |
| TEST-002 | AI evaluation harness (fixed sets, recorded scores per prompt version and model) | AI-002 | Eval runs reproducibly; results stored | Harness run | P1 | BLOCKED | PROPOSED-TASK |

### Identity, tenancy, access (F-CORE-01 to 04, F-SEN-01)

| ID | Objective and value | Depends on | Acceptance criteria | Required tests | Pri | Status | Approval |
|---|---|---|---|---|---|---|---|
| AUTH-001 | Authentication (F-CORE-01) | DB-001 | Register, sign in, sign out; sessions expire; passwords or OAuth handled safely | Unit and integration; negative cases | P0 | BLOCKED | APPROVED-SCOPE |
| AUTH-002 | Workspaces and server-side tenant scoping (F-CORE-02) | AUTH-001 | Every tenant query scoped by session-derived workspace | Isolation tests (TEST-001) | P0 | BLOCKED | APPROVED-SCOPE |
| AUTH-003 | Basic RBAC (F-CORE-04, F-SEN-01) | AUTH-002 | Roles Owner, Admin, Editor, Approver, Viewer enforced | Permission matrix tests | P1 | BLOCKED | APPROVED-SCOPE (roles list is proposed) |

### Integrations and agent runtime (F-CORE-03, F-CORE-05)

| ID | Objective and value | Depends on | Acceptance criteria | Required tests | Pri | Status | Approval |
|---|---|---|---|---|---|---|---|
| INT-001 | Connector framework with encrypted token storage; `ManualPublish` connector | AUTH-002 | Connect, refresh, revoke a connection; tokens never logged; a manually published item is recorded | Integration test; log scan | P1 | BLOCKED | APPROVED-SCOPE |
| INT-002 | Meta Graph connector (Instagram and Facebook Pages), development mode first; verify app-review requirements and limits | INT-001, SEN-001 | Sandbox publish works only through an approved Sentinel request | Integration test with a test page; provider documentation checked | P2 | BLOCKED | APPROVED-SCOPE |
| INT-003 | `Mailer` interface over SMTP (Mailpit in development, a free-tier relay in production); email verification and notifications; SPF and DKIM | AUTH-001, DEC-005 | Verification email delivered to a real inbox in staging | Delivery test | P1 | BLOCKED | PROPOSED-TASK |
| INT-004 | `Storage` interface: local volume backend first; Garage S3-compatible backend (verify presigned URLs and multipart support) | REPO-001 | Upload, download and delete work on both backends; size and type limits enforced | Integration and negative tests | P2 | BLOCKED | PROPOSED-TASK |
| AI-001 | Agent task runtime: queue, retries, step limits, traces, idempotency, dedicated `llm` queue with concurrency limit | API-001 | Failed step retries then surfaces; no duplicate side effects on retry; LLM calls never exceed the configured concurrency | Failure-injection tests | P1 | BLOCKED | APPROVED-SCOPE |
| AI-002 | LLM client abstraction (OpenAI-compatible adapter for Ollama, llama.cpp, vLLM) with structured-output validation and one bounded repair retry | REPO-001, INFRA-002 | Invalid output rejected and retried once, then the step fails visibly; server unavailable fails visibly with no canned output; provider swappable by configuration | Unit tests with recorded fixtures (labeled as mocks); a real run against the dev model | P1 | BLOCKED | PROPOSED-TASK |

### Modules (initial)

| ID | Objective and value | Depends on | Acceptance criteria | Required tests | Pri | Status | Approval |
|---|---|---|---|---|---|---|---|
| CLA-001 | Brand profile capture and storage (F-CLA-01) | AUTH-002, AI-002 | Profile created, versioned, approved by owner | API and UI tests | P1 | BLOCKED | APPROVED-SCOPE |
| CLA-002 | Brand consistency scoring (F-CLA-02) | CLA-001 | Scores returned with guidance; evaluated on a fixed set | TEST-002 eval | P1 | BLOCKED | APPROVED-SCOPE |
| MUS-001 | On-brand content generation (F-MUS-01) | CLA-002, AI-001 | Drafts generated, scored, low scores rewritten up to a cap | Eval plus failure tests | P1 | BLOCKED | APPROVED-SCOPE |
| SEN-001 | Minimal approval step: request, approve or reject, audit record (subset of F-SEN-02, F-SEN-03) | AUTH-003, DEC-003 | No publish or send occurs without a recorded approval; approval and decision stored | Tests proving bypass is impossible | P0 | BLOCKED (DEC-003) | APPROVED-SCOPE (constraint C-01); minimal-in-Phase-1 is PROPOSED-TASK |
| MUS-002 | Scheduling and publishing through one connector (F-MUS-03, F-MUS-04) | MUS-001, SEN-001, INT-001 | Approved item publishes on schedule; unapproved item cannot | Integration test with sandbox connector | P1 | BLOCKED | APPROVED-SCOPE |
| ORB-001 | Goal intake and plan proposal (F-ORB-01) | CLA-001, AI-001 | Goal becomes a typed, reviewable plan; owner approves before execution | Plan-validity eval; loop and step-limit tests | P1 | BLOCKED | APPROVED-SCOPE |
| ORB-002 | Initial Orbit dashboard (F-ORB-03) | ORB-001 | Shows goals, tasks, pending approvals, results | UI tests; empty and error states | P1 | BLOCKED | APPROVED-SCOPE |
| CON-001 | Lead capture and unified inbox (F-CON-01) | AUTH-002, INT-001 | Leads from a form arrive tagged by source | Integration tests; spam and validation cases | P1 | BLOCKED | APPROVED-SCOPE |
| CON-002 | Lead scoring, contact profiles, pipeline (F-CON-02, F-CON-03) | CON-001 | Leads scored and moved through stages | Unit and API tests | P2 | BLOCKED | APPROVED-SCOPE |
| UI-001 | Application shell, navigation, auth screens, approval inbox | AUTH-001 | Screens match flows; loading, empty, error states | UI and accessibility checks | P1 | BLOCKED | PROPOSED-TASK |

### Integration and delivery

| ID | Objective and value | Depends on | Acceptance criteria | Required tests | Pri | Status | Approval |
|---|---|---|---|---|---|---|---|
| E2E-001 | End-to-end MVP loop (section 3) | All P1 Phase 1 tasks | Loop completes in staging with real data; approvals enforced | End-to-end test | P1 | BLOCKED | PROPOSED-TASK |
| DEPLOY-001 | Staging auto-deploy on merge (SSH, `docker compose pull`); production only through a manually triggered workflow; backup taken before production migrations | INFRA-001, INFRA-003 | Tests gate deploys; rollback documented and tried; production cannot deploy without the manual trigger | Deploy and rollback rehearsal | P1 | BLOCKED | PROPOSED-TASK |

---

## 7. Later phases (coarse; refine before starting)

| ID | Objective | Features | Phase | Pri | Status | Approval |
|---|---|---|---|---|---|---|
| SEVA-002 | Map the 75-day window onto Phase 1 tasks; cut scope to fit two people | n/a | 1-S | P1 | BACKLOG | PROPOSED-TASK |
| SEVA-003 | Pilot with a few real businesses; record honest results | n/a | 1-S | P1 | BACKLOG | PROPOSED-TASK |
| SEN-002 | Full configurable approvals and audit viewer | F-SEN-02, F-SEN-03 | 2 | P1 | BACKLOG | APPROVED-SCOPE |
| MKT-001 | Catalog, orders, inventory | F-MKT-01, F-MKT-02 | 2 | P2 | BACKLOG | APPROVED-SCOPE |
| MKT-003 | Razorpay payments (free to integrate; per-transaction fees apply, verify). Dropped if it conflicts with the free-only rule | F-MKT | 2 | P3 | BACKLOG | PROPOSED-TASK |
| INFRA-005 | Point-in-time recovery (WAL archiving), Grafana + Loki + Prometheus if needed | n/a | 2 | P2 | BACKLOG | PROPOSED-TASK |
| PUL-001 | Engagement tracking | F-PUL-01 | 2 | P2 | BACKLOG | APPROVED-SCOPE |
| CLA-003 | AI-visibility tracking (blocked by RES-001 findings) | F-CLA-03, F-CLA-04 | 2 | P2 | BACKLOG | APPROVED-SCOPE |
| CON-003 | Nurture and follow-up agent | F-CON-04 | 2 | P2 | BACKLOG | APPROVED-SCOPE |
| ORB-003 | Full goal-driven orchestration across modules | F-ORB-02 | 3 | P2 | BACKLOG | APPROVED-SCOPE |
| ORB-004 | Shared workspace memory | F-ORB-06 | 3 | P2 | BACKLOG | APPROVED-SCOPE |
| MKT-002 | Customer support agent (grounded answers) | F-MKT-03 | 3 | P2 | BACKLOG | APPROVED-SCOPE |
| CON-004 | Reply handling | F-CON-05 | 3 | P2 | BACKLOG | APPROVED-SCOPE |
| MUS-003 | Auto-generated visibility fixes | F-MUS-02 | 3 | P3 | BACKLOG | APPROVED-SCOPE |
| PUL-002 | Forecasting, experiments, anomaly detection | F-PUL-02 to 04 | 4 | P3 | BACKLOG | APPROVED-SCOPE |
| PUL-003 | Competitor and market watch | F-PUL-05 | 4 | P3 | BACKLOG | APPROVED-SCOPE (placement undecided) |
| ORB-005 | Weekly summary and business ops alerts | F-ORB-04, F-ORB-05 | 4 | P3 | BACKLOG | APPROVED-SCOPE |
| CON-005 | Booking, cold-lead re-engagement | F-CON-06, F-CON-07 | 4 | P3 | BACKLOG | APPROVED-SCOPE |
| CON-006 | WhatsApp channel | F-CON-08 | later | P3 | DEFERRED | PROPOSED-TASK |
| DEPLOY-002 | Beta hardening: security review, performance, billing, runbooks | n/a | 5 | P2 | BACKLOG | PROPOSED-TASK |

### Deferred features and reasons

| Item | Reason for deferral |
|---|---|
| Market, Pulse, advanced automation | Not needed to prove the central loop; confirmed spec places them in Phases 2 to 4 |
| AI-visibility tracking | Feasibility depends on legal, reliable platform access (RES-001) |
| WhatsApp channel | Suggested, not confirmed; provider rules unvalidated; likely per-message charges conflict with the free-only rule |
| Razorpay payments | Per-transaction fees; Phase 2 at the earliest (`MKT-003`) |
| Paid LLM APIs | Not used; the free and open-source rule makes a self-hosted model the default |
| Commission-based pricing, native mobile apps, payments handled by Vistaro | Not validated; out of first release |

---

## 8. Undecided items

| Item | Reference | Needed by |
|---|---|---|
| Open-weight LLM model(s) and quantization | OQ-10 / DEC-002 | Before TEST-002 baselines and any pilot |
| VM provider, region and domain | DEC-005 | Before INFRA-001 |
| Off-VM backup destination | DEC-006 | Before INFRA-003 and any production data |
| Anushka Varshney's acknowledgment of the stack | DEC-001 note | Before REPO-001 |
| First niche | OQ-03 / VAL-002 | Before go-to-market work |
| Pricing | OQ-09 | Before beta |
| Tagline | OQ-04 | Before launch materials |
| Competitor watch placement | OQ-06 / DEC-004 | Before Phase 4 |
| Minimal approval in Phase 1 | OQ-07 / DEC-003 | Before SEN-001 and MUS-002 |
| Name clearance | OQ-01 / NAME-001 | Before heavy branding spend |

---

## 9. Blockers

| Blocker | Affects |
|---|---|
| No repository (unverified); `REPO-000` and `REPO-001` not done | All build tasks |
| No VM provider or domain chosen | INFRA-001, INT-003, Google sign-in, staging |
| LLM capacity on a free CPU-only VM unmeasured | AI-002, DEC-002, any pilot |
| Module-name mapping unconfirmed | Naming in code and docs |
| No user evidence | Niche, SEVA submission, prioritization |
| AI-platform access unverified | CLA-003 |

---

## 10. Next recommended action

1. Anushka Varshney acknowledges `ARCHITECTURE.md` v1.1 (`DEC-001` note).
2. Founders confirm module-name mapping and share the full feature report (`DOC-001`); start owner interviews (`VAL-001`) in parallel.
3. Decide the minimal-approval question (`DEC-003`), the VM provider and domain (`DEC-005`) and the backup destination (`DEC-006`).
4. Run `REPO-000`, then create the repository with CI and the licence check (`REPO-001`).
5. In parallel, stand up the local LLM server and measure it (`INFRA-002`), then choose the model (`DEC-002`).
6. The first coding task should be `DB-001` and `AUTH-001`, with `TEST-001` isolation tests written alongside.

---

## 11. Change log

| Date | Change | By |
|---|---|---|
| 2026-10-17 | Initial roadmap created from the two master documents; no repository inspected | AI-generated, pending founder review |
| 2026-10-22 | Stack finalized as free and open source only (`ARCHITECTURE.md` v1.1). `DEC-001` done; `DEC-002` redefined as open-weight model selection; added `DEC-005`, `DEC-006`, `INFRA-002` to `INFRA-005`, `INT-002` to `INT-004`, `MKT-003`; revised `REPO-001`, `INFRA-001`, `AI-001`, `AI-002`, `DEPLOY-001`; updated blockers and next actions | AI-generated on Dimple's instruction; Anushka's acknowledgment pending |
