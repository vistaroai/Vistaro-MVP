# PROJECT WARNINGS — Vistaro

Central register of warnings, constraints, known issues and technical debt. Last updated: 2026-10-18.
Rules: `/CLAUDE.md` §7. Roadmap: `/docs/PROJECT_ROADMAP.md`.

## How to read this register

Every entry has one **Type**:

| Type | Meaning |
|---|---|
| `CONSTRAINT` | A requirement the founders confirmed. Verified from the project record. |
| `PREVENTIVE` | A control against a risk that has **not** been observed. Not a defect. |
| `OBSERVED` | A real discrepancy or issue actually seen. |
| `UNVERIFIED-DEPENDENCY` | Something the plan relies on that has not been confirmed to work. |

**Severity:** `CRITICAL` (could cause data loss, security breach, or unauthorized public or financial action), `HIGH`, `MEDIUM`, `LOW`.

**State of evidence at creation:** no repository, code, logs, or test results were available. Therefore **there are no observed code defects in this register**. Entries about code are preventive. Do not read severity as proof that a problem exists.

**Maintenance:** add new issues with evidence; never silently delete; close only after verified fix and keep history in the Status field.

---

## A. Critical safety warnings

| ID | Sev | Type | Description | Affected | Impact | Recommended control | Status | Verification required |
|---|---|---|---|---|---|---|---|---|
| WARN-A-001 | CRITICAL | PREVENTIVE | Secrets or API keys committed to source control | Whole repo | Account compromise, cost abuse | Secrets only in environment or secret manager; `.env.example` with names only; secret scanning in CI | Open (control not yet in place; no repo) | Secret scan passes in CI |
| WARN-A-002 | CRITICAL | PREVENTIVE | Destructive database operations (drop, truncate, reset, mass update) without authorization and recovery plan | Database | Permanent data loss | Explicit founder approval; backup first; rollback plan; never run on production casually | Open | Backup restore tested |
| WARN-A-003 | CRITICAL | PREVENTIVE | Casual production deployments or migrations | Production | Outage, data loss | Staging first; manual promotion; rollback rehearsal | Open | Rollback rehearsal recorded |
| WARN-A-004 | CRITICAL | CONSTRAINT | Public, outbound, or financial actions executing without approval | Muse, Convert, Market, Orbit | Unauthorized posts or messages to customers, reputational and legal harm | Route all such actions through Sentinel approval and audit (C-01, C-04); tests that prove bypass is impossible | Open (Sentinel not built) | Bypass-attempt tests |
| WARN-A-005 | CRITICAL | PREVENTIVE | Authentication or authorization bypassed to make a feature work | Auth, RBAC | Unauthorized access | Never weaken checks; review any change touching auth | Open | Permission tests |
| WARN-A-006 | CRITICAL | PREVENTIVE | Overwriting or discarding user changes (hard reset, force push, checkout of modified files) | Repo working tree | Lost work | Check `git status`; never discard without explicit permission | Open | n/a |
| WARN-A-007 | HIGH | PREVENTIVE | Running shell commands whose effect is not understood (recursive deletes, piping remote scripts) | Dev environment | Data loss, compromise | Read before running; prefer dry-run; ask when unsure | Open | n/a |

---

## B. Architecture warnings

| ID | Sev | Type | Description | Affected | Impact | Recommended control | Status | Verification required |
|---|---|---|---|---|---|---|---|---|
| WARN-B-001 | HIGH | CONSTRAINT | Sentinel must not be bypassed; it is the single enforcement point for permissions, approvals and audit | All modules | Governance breaks | Call Sentinel from every consequential path; no module-local approval logic | Open | Tests |
| WARN-B-002 | HIGH | CONSTRAINT | Orbit coordinates modules and must not replace or absorb their logic; each module owns its domain data (C-02, C-03) | Orbit and modules | Tangled boundaries | Access other modules through interfaces, not their tables | Open | Review of imports and queries |
| WARN-B-003 | HIGH | OBSERVED | Open design conflict (OQ-07): the founders' spec puts approvals in Phase 2, but approvals are mandatory for public actions. Phase 1 modules that publish or send would violate the rule if built first | Muse, Convert, Sentinel | Rule breach if unresolved | Build the minimal approval step (`SEN-001`) in Phase 1, as decided in `DEC-003` (2026-10-18) | Mitigated by decision; open until `SEN-001` is verified | Approval-bypass tests |
| WARN-B-004 | MEDIUM | CONSTRAINT | Technology stack was undecided until 2026-10-18; it is now decided in `docs/ARCHITECTURE.md` but **unverified in practice** | All build work | Rework if assumed | Follow `docs/ARCHITECTURE.md`; verify during `REPO-001` and `INFRA-001` | Resolved by decision `DEC-001`; keep until the repository confirms it | Repository matches the ADRs |
| WARN-B-005 | MEDIUM | PREVENTIVE | Free-form agent-to-agent chat can create loops and conflicting actions | Orbit, agents | Runaway cost, duplicate actions | Planner-executor with typed steps, step limits, single task store | Open | Loop and step-limit tests |
| WARN-B-006 | MEDIUM | PREVENTIVE | Duplicate implementations of brand scoring or approval logic across modules | Clarity, Sentinel | Inconsistent behavior | Reuse the single implementation | Open | Code review |
| WARN-B-007 | MEDIUM | PREVENTIVE | Breaking API or schema changes without a path | API, DB | Client breakage | Version APIs; reversible migrations | Open | Contract tests |
| WARN-B-008 | LOW | PREVENTIVE | Circular dependencies between modules | Modules | Fragile builds | Keep dependency direction per master doc §15.8 | Open | Dependency check |
| WARN-B-009 | HIGH | PREVENTIVE | RLS tenant setting applied at connection level instead of transaction level; with pooled connections one request can inherit another tenant's setting | Database access layer | Cross-tenant data exposure | Use transaction-local `set_config(..., true)` only; wrap every request and task in one transaction; isolation tests | Open | `TEST-001` isolation tests, including pooled-connection reuse |
| WARN-B-010 | MEDIUM | PREVENTIVE | Celery misconfiguration (acks late, visibility timeout shorter than long steps, retries without idempotency) causes duplicate or lost steps | Agent runtime | Duplicate posts or messages, stalled goals | Idempotency keys, atomic claim, timeout longer than the longest step, reaper for stale tasks, DB as source of truth | Open | Failure-injection tests |
| WARN-B-011 | MEDIUM | PREVENTIVE | Own session-based authentication (ADR-007) carries implementation risk | Auth | Account takeover | Use vetted libraries (Argon2id, Authlib); `SEC-001` baseline; independent review in `SEC-002` | Open | Auth tests; security review |
| WARN-B-012 | LOW | PREVENTIVE | `import-linter` contracts drift or are disabled, eroding module boundaries | Whole backend | Tangled modules | Run in CI; changes to contracts need review | Open | CI shows contracts enforced |

---

## C. Feature-specific warnings

| ID | Sev | Type | Description | Affected | Impact | Recommended control | Status | Verification required |
|---|---|---|---|---|---|---|---|---|
| WARN-C-001 | HIGH | UNVERIFIED-DEPENDENCY | The AI-visibility feature assumes AI-platform answers (ChatGPT, Gemini, Perplexity, Google AI Overviews) can be obtained legally and reliably. This is **not confirmed** (A-05, OQ-05) | Clarity (F-CLA-03) | Feature may be infeasible or violate platform terms | Complete `RES-001` before building; do not scrape in violation of terms; never present simulated results as real | Open | Research findings with sources |
| WARN-C-002 | HIGH | PREVENTIVE | AI outputs can be wrong or invented, especially in customer-facing replies | Support agent, Convert | False promises, lost trust | Grounding in store data; escalate when ungrounded; evaluation sets | Open | Groundedness evals |
| WARN-C-003 | HIGH | PREVENTIVE | AI-platform results vary between runs | Clarity | Misleading single results | Repeat runs; report rates with sample sizes | Open | Variation test |
| WARN-C-004 | HIGH | PREVENTIVE | Prompt injection via inbound customer text | Convert, support | Agent misled or misused | Treat inbound text as data; limit tools; validate outputs | Open | Injection test set |
| WARN-C-005 | MEDIUM | UNVERIFIED-DEPENDENCY | Social and messaging API approvals, permissions, rate limits and costs are unknown (Meta, WhatsApp) | Muse, Convert | Delays or reduced scope | Apply early; use clearly labeled sandbox data meanwhile | Open | Provider documentation check |
| WARN-C-006 | MEDIUM | PREVENTIVE | Messaging consent and opt-out obligations | Convert | Legal and deliverability issues | Track opt-in and opt-out; honor them; obtain advice (`LEGAL-001`) | Open | Consent tests |
| WARN-C-007 | MEDIUM | PREVENTIVE | Lead duplicates across channels | Convert | Wrong merges | Human review of ambiguous merges | Open | Dedup tests |
| WARN-C-008 | LOW | CONSTRAINT | WhatsApp channel and Hindi-English content are suggestions, not confirmed features | Convert, Muse | Building unapproved scope | Treat as `PROPOSED` until approved | Open | n/a |
| WARN-C-009 | MEDIUM | UNVERIFIED-DEPENDENCY | Razorpay onboarding, compliance, and fees for the Market module are unverified | Market (`MKT-003`) | Delays or compliance gaps | Verify in `MKT-003`; start in test mode; take advice in `LEGAL-001` | Open | Provider documentation check |
| WARN-C-010 | MEDIUM | PREVENTIVE | LLM-based brand scoring may disagree with the owner's judgment | Clarity | Wrong rewrites or approvals | Deterministic checks first; labeled eval set; record agreement; owner always approves | Open | `CLA-002` eval results |
| WARN-C-011 | MEDIUM | PREVENTIVE | A planner could propose actions outside the allowed set or try to skip approvals | Orbit | Unsafe plans | Registry whitelist; approval requirement set by registry, not by the model; deterministic plan validation | Open | Plan-validation tests |

---

## D. Database and data-integrity warnings

| ID | Sev | Type | Description | Affected | Impact | Recommended control | Status | Verification required |
|---|---|---|---|---|---|---|---|---|
| WARN-D-001 | CRITICAL | PREVENTIVE | Missing `workspace_id` scoping lets one business read another's data | All tenant tables | Privacy breach | Server-derived scope on every query; row-level security; isolation tests | Open | `TEST-001` isolation tests |
| WARN-D-002 | HIGH | PREVENTIVE | Migrations without rollback or tested on unrealistic data | Database | Failed deploys, data loss | Reversible migrations; test on realistic copy | Open | Up and down test |
| WARN-D-003 | HIGH | PREVENTIVE | No backups or untested restores | Production DB | Unrecoverable loss | Daily backups; periodic restore test | Open | Restore test recorded |
| WARN-D-004 | MEDIUM | PREVENTIVE | Audit logs modifiable or incomplete | Sentinel | Loss of accountability | Append-only; completeness tests | Open | Audit completeness test |
| WARN-D-005 | MEDIUM | PREVENTIVE | Retention and deletion periods undefined | Conversations, contacts | Over-retention or accidental deletion | Define retention (`LEGAL-001`); deletion on request | Open | Retention policy recorded |
| WARN-D-006 | LOW | PREVENTIVE | Missing indexes on high-volume lookups (leads, messages, metrics) | Convert, Pulse | Slow queries | Add indexes from measured query plans, not guesses | Open | Query plan review |
| WARN-D-007 | MEDIUM | PREVENTIVE | The `sessions` table is looked up before a workspace is known, so it is not workspace-scoped by RLS | Auth | Session misuse if scoping by user is wrong | Scope by `user_id` in code; hash session IDs; document the exception; test it | Open | Session scoping tests |
| WARN-D-008 | LOW | PREVENTIVE | `audit_logs`, `agent_runs`, and metrics tables grow without bound | Database | Slow queries, cost | Retention policy; partitioning when measured need appears | Open | Size monitoring |

---

## E. Security and privacy warnings

| ID | Sev | Type | Description | Affected | Impact | Recommended control | Status | Verification required |
|---|---|---|---|---|---|---|---|---|
| WARN-E-001 | HIGH | PREVENTIVE | Integration tokens stolen or logged | Connectors | Account takeover on customers' channels | Encrypt at rest; least privilege; rotation; never log | Open | Log scan; token handling review |
| WARN-E-002 | HIGH | PREVENTIVE | Personal data of customers in logs, fixtures, prompts sent to providers, or docs | Logging, AI calls | Privacy breach | Redact; minimize what is sent to LLM providers; synthetic fixtures | Open | Log and fixture review |
| WARN-E-003 | MEDIUM | PREVENTIVE | Unvalidated input and file uploads (brand assets, lead forms) | API | Injection, malware, abuse | Validate and size-limit; scan uploads; rate limit | Open | Negative tests |
| WARN-E-004 | MEDIUM | PREVENTIVE | Third-party data sharing without consent or understanding | LLM and platform providers | Legal exposure | Document what data goes to which provider | Open | Data-flow doc |
| WARN-E-005 | MEDIUM | UNVERIFIED-DEPENDENCY | Applicability of India's data protection law and platform terms to Vistaro is not assessed (R-09) | Whole product | Compliance gaps | `LEGAL-001` | Open | Advisor input |
| WARN-E-006 | LOW | PREVENTIVE | Session and token handling weaknesses | Auth | Session hijack | Short-lived tokens; secure cookies | Open | Auth review |

---

## F. Reliability and deployment warnings

| ID | Sev | Type | Description | Affected | Impact | Recommended control | Status | Verification required |
|---|---|---|---|---|---|---|---|---|
| WARN-F-001 | HIGH | PREVENTIVE | Retries causing duplicate posts or messages | Agent runtime, connectors | Customers receive duplicates | Idempotency keys; idempotent steps | Open | Failure-injection test |
| WARN-F-002 | MEDIUM | PREVENTIVE | External outages and rate limits (LLM, social, messaging) | Agents | Stalled tasks | Timeouts, capped retries with backoff, visible failure state, circuit breaker | Open | Outage simulation |
| WARN-F-003 | MEDIUM | PREVENTIVE | Uncontrolled model cost | Agents | Unexpected bill | Per-workspace budgets; step limits; caching | Open | Cost tracking |
| WARN-F-004 | MEDIUM | PREVENTIVE | Environment drift between dev, staging, production | Deploy | Works locally, fails live | Documented env variables; infrastructure as code where practical | Open | Staging smoke tests |
| WARN-F-005 | MEDIUM | PREVENTIVE | No monitoring or alerts | Operations | Silent failures | Logs, traces, alerts on failures and cost | Open | Alert test |
| WARN-F-006 | LOW | PREVENTIVE | Two-person team: bus factor of two | Whole project | Stalls | Keep docs current; simple architecture | Open | n/a |
| WARN-F-007 | MEDIUM | UNVERIFIED-DEPENDENCY | Hosting plan, region, credits, and `pgvector` availability on Render are unverified | Infrastructure | Rework or cost surprise | Verify in `INFRA-001`; containers keep the move to another host cheap | Open | Findings recorded in `INFRA-001` |
| WARN-F-008 | LOW | PREVENTIVE | Single instance each of API, worker, and beat at launch means no high availability | Operations | Downtime during failures or deploys | Accept for MVP; backups and rollback rehearsal; scale per ARCHITECTURE §15 | Open | Rollback rehearsal |

---

## G. Known bugs and technical debt

### G.1 Code defects

**None recorded.** No code was inspected. When a defect is found, add it here with the fields below.

Template:

| Field | Content |
|---|---|
| Warning ID | `WARN-G-NNN` |
| Severity | CRITICAL / HIGH / MEDIUM / LOW |
| Description | |
| Evidence or reproduction steps | |
| Affected components | |
| User or business impact | |
| Workaround | |
| Recommended fix | |
| Status | |
| Verification required | |

### G.2 Observed documentation and planning discrepancies

These are real, observed issues in the project record, not hypothetical.

| ID | Sev | Type | Description and evidence | Affected | Impact | Workaround | Recommended fix | Status | Verification |
|---|---|---|---|---|---|---|---|---|---|
| WARN-G-001 | MEDIUM | OBSERVED | **Module naming inconsistency.** Early planning used Lens, Dream, Lead Master, Store Manager, Engagement Tracking; the founders' later report uses Clarity, Muse, Convert, Market, Pulse, plus Sentinel. The mapping between them was inferred, not confirmed. Evidence: the two naming sets in the project record | Docs, future code names | Confusing code and docs | Use canonical names; note old name once | `DOC-001`: founders confirm mapping and share the full report | Open | Founders confirm in writing |
| WARN-G-002 | MEDIUM | OBSERVED | **SEVA dossier draft (chat) is out of date.** The draft of Point 11 proposed a five-role team and used the early module names; the team has two members. Evidence: the SEVA draft versus the team record | SEVA submission | Inaccurate submission | Rewrite before submitting | Update Point 11 and module names in the dossier and deck | Open | Dossier reviewed |
| WARN-G-003 | LOW | OBSERVED | **Illustrative "challenges" write-up is not real.** A draft "Challenges we ran into" was explicitly illustrative; it must not be submitted as real build history | SEVA submission | Misleading claims | Replace with real challenges once building | Rewrite from actual events | Open | n/a |
| WARN-G-004 | MEDIUM | OBSERVED | **Phase plan versus rule.** See WARN-B-003 (approvals in Phase 2 vs mandatory approvals) | Roadmap | Rule breach | `DEC-003` | Resolved by decision; implementation pending (`SEN-001`) | Decision recorded; tests pending |
| WARN-G-005 | LOW | OBSERVED | **Full Product Features report not seen by the authors of the master docs.** Only a summary was available | Master docs | Possible scope mismatch | Compare when available | `DOC-001` | Open | Diff reviewed |
| WARN-G-006 | LOW | OBSERVED | **Tagline and logo unfinished**; only candidates and a prompt exist | Branding | None for engineering | Do not hardcode a tagline or logo as final | Founders decide | Open | n/a |
| WARN-G-007 | LOW | OBSERVED | **LLM default was recommended by an Anthropic model** and has not been independently evaluated (disclosed in ARCHITECTURE.md) | AI layer | Possible suboptimal provider choice | Provider-agnostic interface | `DEC-002` evaluation on a fixed task set | Open | Evaluation recorded |
| WARN-G-008 | MEDIUM | OBSERVED | **Documents were generated without a repository.** Every implementation statement is unverified; commands in the guide are targets | All docs | Docs may not match reality once code exists | Run `REPO-000`; record verified commands | `REPO-000`, `REPO-001` | Open | Verified commands recorded |

---

## Change log

| Date | Change |
|---|---|
| 2026-10-17 | Initial register created. No code defects recorded because no repository was inspected. Preventive controls clearly labeled. |
| 2026-10-18 | Updated for the decided stack: resolved or mitigated stack-related entries; added WARN-B-009 to B-012, C-009 to C-011, D-007, D-008, F-007, F-008, G-007, G-008. |
