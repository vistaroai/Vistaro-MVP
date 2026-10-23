# PROJECT WARNINGS — Vistaro

Central register of warnings, constraints, known issues and technical debt. Last updated: 2026-10-22 (stack finalized as free and open source only).
Rules: `/CLAUDE.md` §7. Roadmap: `/docs/PROJECT_ROADMAP.md`. Architecture: `/docs/ARCHITECTURE.md` v1.1.

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
| WARN-A-001 | CRITICAL | PREVENTIVE | Secrets or API keys committed to source control | Whole repo | Account compromise, cost abuse | Secrets only in SOPS-encrypted files or restricted environment files; never the age private key; `.env.example` with names only; secret scanning in CI | Open (control not yet in place; no repo) | Secret scan passes in CI |
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
| WARN-B-003 | HIGH | OBSERVED | Open design conflict (OQ-07): the founders' spec puts approvals in Phase 2, but approvals are mandatory for public actions. Phase 1 modules that publish or send would violate the rule if built first | Muse, Convert, Sentinel | Rule breach if unresolved | Decide `DEC-003`; recommended: minimal approval step in Phase 1 | Open | Decision recorded |
| WARN-B-004 | MEDIUM | CONSTRAINT | ~~Technology stack is undecided.~~ **Resolved 2026-10-22:** the stack is decided in `ARCHITECTURE.md` v1.1 (`DEC-001` done). Remaining rule: do not swap any ADR decision without a proposal (`CLAUDE.md` §9) | All build work | Rework if the stack drifts | Follow `ARCHITECTURE.md`; ADR for any change | Closed (history kept: was Open since 2026-10-17) | Decision recorded in roadmap |
| WARN-B-005 | MEDIUM | PREVENTIVE | Free-form agent-to-agent chat can create loops and conflicting actions | Orbit, agents | Runaway cost, duplicate actions | Planner-executor with typed steps, step limits, single task store | Open | Loop and step-limit tests |
| WARN-B-006 | MEDIUM | PREVENTIVE | Duplicate implementations of brand scoring or approval logic across modules | Clarity, Sentinel | Inconsistent behavior | Reuse the single implementation | Open | Code review |
| WARN-B-007 | MEDIUM | PREVENTIVE | Breaking API or schema changes without a path | API, DB | Client breakage | Version APIs; reversible migrations | Open | Contract tests |
| WARN-B-008 | LOW | PREVENTIVE | Circular dependencies between modules | Modules | Fragile builds | Keep dependency direction per `ARCHITECTURE.md` §2.2 (enforced by import-linter) | Open | Dependency check |
| WARN-B-009 | MEDIUM | CONSTRAINT | **Free and open source only** (founder instruction 2026-10-22). Adding a dependency, container image, model or font with a source-available, non-commercial or restricted licence, or one whose free use can be withdrawn, breaks the rule. Examples to avoid: Redis under its newer licences (use Valkey), Sentry self-hosted, MinIO community edition (status uncertain, verify), models with usage restrictions | Whole repo, images, models | Rework, legal exposure, broken founder requirement | Licence allow-list (`ARCHITECTURE.md` §0); CI licence check (ADR-021); ADR for any exception; check each model's licence file | Open (CI check not yet built, `REPO-001`) | Licence check fails on a deliberate bad dependency |

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
| WARN-C-009 | HIGH | PREVENTIVE | Small self-hosted open-weight models are less reliable than large hosted models: invalid JSON, weak plans, off-brand or poorer Hindi-English text | Orbit, Clarity, Muse, Convert | Failed steps, poor content, user distrust | Grammar or JSON-schema constrained decoding; Pydantic validation; one bounded repair retry; deterministic checks first (brand and lead scoring); fixed eval sets per model and prompt version; fail visibly, never fake output | Open | `TEST-002` evals pass on the chosen model (`DEC-002`) |
| WARN-C-010 | MEDIUM | UNVERIFIED-DEPENDENCY | Some planned integrations are free to integrate but not free to use: Razorpay (per-transaction fees), WhatsApp Cloud API (per-message charges). Meta, Google and SMTP free tiers have limits that may change | Market, Convert, Muse | Conflict with the free-only rule; surprise costs | Keep them optional and behind interfaces; Phase 2 and later; verify pricing at `MKT-003`, `CON-006`, `INT-002`, `INT-003`; drop if they cannot be free | Open | Provider pricing checked and dated |

---

## D. Database and data-integrity warnings

| ID | Sev | Type | Description | Affected | Impact | Recommended control | Status | Verification required |
|---|---|---|---|---|---|---|---|---|
| WARN-D-001 | CRITICAL | PREVENTIVE | Missing `workspace_id` scoping lets one business read another's data | All tenant tables | Privacy breach | Server-derived scope on every query; row-level security; isolation tests | Open | `TEST-001` isolation tests |
| WARN-D-002 | HIGH | PREVENTIVE | Migrations without rollback or tested on unrealistic data | Database | Failed deploys, data loss | Reversible migrations; test on realistic copy | Open | Up and down test |
| WARN-D-003 | CRITICAL | PREVENTIVE | No backups or untested restores. **Severity raised from HIGH on 2026-10-22:** the stack is self-hosted, so there is no managed-database backup safety net | Production DB, stored files | Unrecoverable loss | Nightly `pg_dump` plus encrypted restic copy to a location off the VM (`DEC-006`, `INFRA-003`); monthly restore test; backup before every production migration | Open | Restore test recorded |
| WARN-D-004 | MEDIUM | PREVENTIVE | Audit logs modifiable or incomplete | Sentinel | Loss of accountability | Append-only; completeness tests | Open | Audit completeness test |
| WARN-D-005 | MEDIUM | PREVENTIVE | Retention and deletion periods undefined | Conversations, contacts | Over-retention or accidental deletion | Define retention (`LEGAL-001`); deletion on request | Open | Retention policy recorded |
| WARN-D-006 | LOW | PREVENTIVE | Missing indexes on high-volume lookups (leads, messages, metrics) | Convert, Pulse | Slow queries | Add indexes from measured query plans, not guesses | Open | Query plan review |

---

## E. Security and privacy warnings

| ID | Sev | Type | Description | Affected | Impact | Recommended control | Status | Verification required |
|---|---|---|---|---|---|---|---|---|
| WARN-E-001 | HIGH | PREVENTIVE | Integration tokens stolen or logged | Connectors | Account takeover on customers' channels | Encrypt at rest; least privilege; rotation; never log | Open | Log scan; token handling review |
| WARN-E-002 | HIGH | PREVENTIVE | Personal data of customers in logs, fixtures, prompts sent to providers, or docs | Logging, AI calls | Privacy breach | Redact; minimize what is sent to LLM providers; synthetic fixtures | Open | Log and fixture review |
| WARN-E-003 | MEDIUM | PREVENTIVE | Unvalidated input and file uploads (brand assets, lead forms) | API | Injection, malware, abuse | Validate and size-limit; scan uploads; rate limit | Open | Negative tests |
| WARN-E-004 | MEDIUM | PREVENTIVE | Third-party data sharing without consent or understanding. Inference now stays on our own server; remaining recipients are Meta, Google, the SMTP relay, Razorpay and GitHub | Platform and relay providers | Legal exposure | Document what data goes to which provider | Open | Data-flow doc |
| WARN-E-005 | MEDIUM | UNVERIFIED-DEPENDENCY | Applicability of India's data protection law and platform terms to Vistaro is not assessed (R-09) | Whole product | Compliance gaps | `LEGAL-001` | Open | Advisor input |
| WARN-E-006 | LOW | PREVENTIVE | Session and token handling weaknesses | Auth | Session hijack | Short-lived tokens; secure cookies | Open | Auth review |
| WARN-E-007 | HIGH | PREVENTIVE | **Self-hosted server hardening.** We now run the host: exposed SSH, open database, Valkey or LLM ports, missing OS updates, or unrotated logs filling the disk | VM, Compose stack | Compromise, data theft, outage | Only ports 80, 443 and key-only SSH open; firewall; internal Docker network for everything else; automatic security updates; fail2ban or equivalent; log rotation; restricted deploy key | Open | External port scan; hardening checklist at `INFRA-001` |
| WARN-E-008 | MEDIUM | PREVENTIVE | SOPS age private key lost or leaked | Secrets | Lost access to secrets, or all secrets exposed | Keep the key off the repo; back it up separately from the data backups; document rotation | Open | Key recovery drill |

---

## F. Reliability and deployment warnings

| ID | Sev | Type | Description | Affected | Impact | Recommended control | Status | Verification required |
|---|---|---|---|---|---|---|---|---|
| WARN-F-001 | HIGH | PREVENTIVE | Retries causing duplicate posts or messages | Agent runtime, connectors | Customers receive duplicates | Idempotency keys; idempotent steps | Open | Failure-injection test |
| WARN-F-002 | MEDIUM | PREVENTIVE | Outages and rate limits: our own LLM server, and external social, messaging and email services | Agents | Stalled tasks | Timeouts, capped retries with backoff, visible failure state ("AI engine unavailable"), circuit breaker; never canned output | Open | Outage simulation |
| WARN-F-003 | MEDIUM | PREVENTIVE | Uncontrolled model usage: runaway loops exhaust the LLM server and slow everyone (no money bill, but shared capacity) | Agents | Starved API and worker, slow responses | Per-workspace token budgets; step limits; caching; dedicated `llm` queue with concurrency limit | Open | Token tracking; load test |
| WARN-F-004 | MEDIUM | PREVENTIVE | Environment drift between dev, staging, production | Deploy | Works locally, fails live | Documented env variables; infrastructure as code where practical | Open | Staging smoke tests |
| WARN-F-005 | MEDIUM | PREVENTIVE | No monitoring or alerts | Operations | Silent failures | Logs, traces, alerts on failures and cost | Open | Alert test |
| WARN-F-006 | LOW | PREVENTIVE | Two-person team: bus factor of two. Self-hosting adds operations work (patching, backups, monitoring) | Whole project | Stalls | Keep docs current; simple architecture; scripts for deploy, backup and restore | Open | n/a |
| WARN-F-007 | HIGH | UNVERIFIED-DEPENDENCY | A free CPU-only VM may not serve an open-weight LLM at usable latency or concurrency. Not measured | Every AI feature | Slow or failing agents; pilot not possible | Measure at `INFRA-002`; use small quantized models; single-concurrency `llm` queue; plan a GPU or second machine if needed; set honest expectations for SEVA and pilots | Open | Measured latency and concurrency report |
| WARN-F-008 | MEDIUM | UNVERIFIED-DEPENDENCY | Free VM tiers may have changing quotas, capacity shortages, idle-instance reclamation or account termination, and no SLA. Not verified | Hosting | Outage or lost host | Read terms at `DEC-005`; keep the stack reproducible from Compose files; off-VM backups; keep one alternative host identified | Open | Terms checked and cited |
| WARN-F-009 | MEDIUM | PREVENTIVE | Staging and production sharing one VM at launch: shared failure, resource contention, risk of touching the wrong environment | Deploy | Staging load or a mistake hurts production | CPU and memory limits per container; separate Compose projects, networks, volumes and secrets; clear environment names; split to a second VM when available | Open | Resource-limit and isolation check |
| WARN-F-010 | LOW | PREVENTIVE | Free VMs are often ARM; some images or Python and Node packages may lack arm64 builds | Build, deploy | Failed builds or deploys | Multi-arch image builds in CI; test on arm64 early | Open | Staging runs on the target architecture |

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
| WARN-G-004 | MEDIUM | OBSERVED | **Phase plan versus rule.** See WARN-B-003 (approvals in Phase 2 vs mandatory approvals) | Roadmap | Rule breach | `DEC-003` | Open | Decision recorded |
| WARN-G-005 | LOW | OBSERVED | **Full Product Features report not seen by the authors of the master docs.** Only a summary was available | Master docs | Possible scope mismatch | Compare when available | `DOC-001` | Open | Diff reviewed |
| WARN-G-006 | LOW | OBSERVED | **Tagline and logo unfinished**; only candidates and a prompt exist | Branding | None for engineering | Do not hardcode a tagline or logo as final | Founders decide | Open | n/a |
| WARN-G-007 | MEDIUM | OBSERVED | **Other documents may still describe the old stack.** `STARTUP_AI_MASTER_CONTEXT.md`, `STARTUP_MASTER_BLUEPRINT.md`, `docs/DEVELOPMENT_GUIDE.md`, `docs/ACTIVE_TASKS.md` and `AGENTS.md` are referenced by `CLAUDE.md` and `ARCHITECTURE.md` but were not provided when the stack was finalized on 2026-10-22, so they were not updated. The master document suggested Redis; v1.0 of the architecture named Render, Cloudflare, Resend, Sentry and Anthropic. The "Vistaro in Plain Language" guide (v1.0) also described those choices | Docs | Contradictory guidance to agents and people | `ARCHITECTURE.md` v1.1 wins (`CLAUDE.md` §1) | Update each file to v1.1 and record the decision in the decision log | Open | Grep of all docs for Render, Cloudflare, Resend, Sentry, Redis, Anthropic returns only history notes |

---

## Change log

| Date | Change |
|---|---|
| 2026-10-17 | Initial register created. No code defects recorded because no repository was inspected. Preventive controls clearly labeled. |
| 2026-10-22 | Stack finalized as free and open source only. Closed WARN-B-004 (stack decided). Added WARN-B-009 (free-only rule), WARN-C-009 and C-010 (small models, not-free integrations), WARN-E-007 and E-008 (self-hosted hardening, age key), WARN-F-007 to F-010 (LLM capacity, free VM terms, shared VM, ARM builds), WARN-G-007 (other docs not updated). Raised WARN-D-003 (backups) from HIGH to CRITICAL. Reworded WARN-A-001, B-008, E-004, F-002, F-003, F-006 for the new stack. No code defects recorded because no repository exists. |
