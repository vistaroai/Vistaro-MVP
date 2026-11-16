# PROJECT WARNINGS — Vistaro

Central register of warnings, constraints, known issues and technical debt. Last updated: 2026-11-16.
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

**State of evidence:** the register was created on 2026-10-18 before any code existed, so the early entries are preventive. Since then code has shipped and some risks have been **observed** for real — `WARN-B-013` (hanging DB probes) is one, and it is marked as such. Read severity as the worst-case impact, not as proof that a problem exists.

**Maintenance:** add new issues with evidence; never silently delete; close only after a verified fix and keep the history in the Status field. Every Status should say what was verified and how; "verified by" can be a commit hash or a `file:line`.

## Summary (2026-11-16)

| Dimension | Count |
|---|---|
| Entries | 72 |
| By section | A 8 · B 16 · C 11 · D 10 · E 9 · F 8 · G 10 |
| By severity | CRITICAL 7 · HIGH 18 · MEDIUM 33 · LOW 14 |
| By type | CONSTRAINT 5 · OBSERVED 16 · PREVENTIVE 44 · UNVERIFIED-DEPENDENCY 7 |
| Resolved | 2 — `WARN-B-008`, `WARN-B-013` |

**Read first:** `WARN-A-004` (nothing may publish without Sentinel), `WARN-B-001`/`WARN-B-006` (one source of role truth), `WARN-D-001` (RLS covers only `memberships`), `WARN-D-009`/`WARN-D-010` (existence-oracle and member-email trade-offs to decide), `WARN-E-008` (staging cookie topology), `WARN-F-007` (mutable local image tag).

---

## A. Critical safety warnings

| ID | Sev | Type | Description | Affected | Impact | Recommended control | Status | Verification required |
|---|---|---|---|---|---|---|---|---|
| WARN-A-001 | CRITICAL | PREVENTIVE | Secrets or API keys committed to source control | Whole repo | Account compromise, cost abuse | Secrets only in environment or secret manager; `.env.example` with names only; secret scanning in CI | Partially addressed: TruffleHog runs in CI (`trufflesecurity/trufflehog@main`, `--results=verified,unknown`) and has been green on every merge since PR #5; `.env.example` is names-only and `.env` is gitignored. Evidence: `.github/workflows/ci.yml` secret-scan job | Secret scan passes in CI |
| WARN-A-002 | CRITICAL | PREVENTIVE | Destructive database operations (drop, truncate, reset, mass update) without authorization and recovery plan | Database | Permanent data loss | Explicit founder approval; backup first; rollback plan; never run on production casually | Open | Backup restore tested |
| WARN-A-003 | CRITICAL | PREVENTIVE | Casual production deployments or migrations | Production | Outage, data loss | Staging first; manual promotion; rollback rehearsal | Open | Rollback rehearsal recorded |
| WARN-A-004 | CRITICAL | CONSTRAINT | Public, outbound, or financial actions executing without approval | Muse, Convert, Market, Orbit | Unauthorized posts or messages to customers, reputational and legal harm | Route all such actions through Sentinel approval and audit (C-01, C-04); tests that prove bypass is impossible | Open (Sentinel not built) | Bypass-attempt tests |
| WARN-A-005 | CRITICAL | PREVENTIVE | Authentication or authorization bypassed to make a feature work | Auth, RBAC | Unauthorized access | Never weaken checks; review any change touching auth | Open | Permission tests |
| WARN-A-006 | CRITICAL | PREVENTIVE | Overwriting or discarding user changes (hard reset, force push, checkout of modified files) | Repo working tree | Lost work | Check `git status`; never discard without explicit permission | Open. Cleaned 2026-11-16: the scratch files left by earlier sessions (`pytest_*.txt`, `test_output.txt`, `tmp_at.txt`) were deleted and the patterns added to `.gitignore`. Keep the tree clean before every reset | n/a |
| WARN-A-007 | HIGH | PREVENTIVE | Running shell commands whose effect is not understood (recursive deletes, piping remote scripts) | Dev environment | Data loss, compromise | Read before running; prefer dry-run; ask when unsure | Open | n/a |
| WARN-A-008 | HIGH | PREVENTIVE | CI executes third-party GitHub Actions through mutable refs, including TruffleHog `@main` and version tags | CI workflow | A tag or branch can move to changed action code without a reviewed commit change | Pin third-party actions to reviewed commit SHAs; review bumps manually (Dependabot disabled 2026-10-28) | Open. All six third-party actions are still mutable refs (`actions/checkout@v7`, `astral-sh/setup-uv@v7`, `actions/upload-artifact@v7`, `actions/download-artifact@v8`, `pnpm/action-setup@v4`, `actions/setup-node@v7`, `trufflesecurity/trufflehog@main`). Note: Dependabot was disabled on 2026-10-28 but its PRs #6–#11 were merged on that same day, after the founders' "no bot-authored commits" rule | Reviewed SHA-pinned action references |

---

## B. Architecture warnings

| ID | Sev | Type | Description | Affected | Impact | Recommended control | Status | Verification required |
|---|---|---|---|---|---|---|---|---|
| WARN-B-001 | HIGH | CONSTRAINT | Sentinel must not be bypassed; it is the single enforcement point for permissions, approvals and audit | All modules | Governance breaks | Call Sentinel from every consequential path; no module-local approval logic | Partially addressed (2026-11-16). `AUTH-003` landed the map (`vistaro/sentinel/permissions.py`) and the `require_permission` dependency in `vistaro/api/deps.py`; `add_member`, `list_members` and `switch_workspace` now enforce a permission from the map instead of an inline role list, and the generated matrix test proves the route table and the registry agree. Still open: approvals and audit (`SEN-001`), and the `add_member` route's permission is the only membership permission enforced | Tests — `tests/test_permission_matrix.py` |
| WARN-B-002 | HIGH | CONSTRAINT | Orbit coordinates modules and must not replace or absorb their logic; each module owns its domain data (C-02, C-03) | Orbit and modules | Tangled boundaries | Access other modules through interfaces, not their tables | Open. Concrete debt: raw `text()` SQL lives in the `api/` modules (`api/deps.py`, `api/workspaces.py`, `api/auth.py`) rather than in repositories, which `CLAUDE.md` rule 19 reserves for repositories. No Orbit code exists yet | Review of imports and queries |
| WARN-B-003 | HIGH | OBSERVED | Open design conflict (OQ-07): the founders' spec puts approvals in Phase 2, but approvals are mandatory for public actions. Phase 1 modules that publish or send would violate the rule if built first | Muse, Convert, Sentinel | Rule breach if unresolved | Build the minimal approval step (`SEN-001`) in Phase 1, as decided in `DEC-003` (2026-10-18) | Mitigated by decision; open until `SEN-001` is verified | Approval-bypass tests |
| WARN-B-004 | MEDIUM | CONSTRAINT | Technology stack was undecided until 2026-10-18; it is decided in `docs/ARCHITECTURE.md` but only the bootstrap is verified in practice | All build work | Rework if assumed | Follow `docs/ARCHITECTURE.md`; verify during `INFRA-001` and each feature task | Partially verified: bootstrap (`REPO-001`), database (`DB-001`), tenancy (`TEST-001`, in CI) and Redis (CI service) are all verified locally and/or in CI. Still unverified: Celery workers (dependency only, no worker/beat file), hosting and staging (`INFRA-001`) | `CLAUDE.md` §12; `INFRA-001` |
| WARN-B-005 | MEDIUM | PREVENTIVE | Free-form agent-to-agent chat can create loops and conflicting actions | Orbit, agents | Runaway cost, duplicate actions | Planner-executor with typed steps, step limits, single task store | Open | Loop and step-limit tests |
| WARN-B-006 | MEDIUM | OBSERVED | Two sources of role truth, or a duplicate implementation of approval logic, across modules | Clarity, Sentinel | Inconsistent behavior | Reuse the single implementation | Observed 2026-11-16 and fixed the same day: `AUTH-003` first shipped only the `ROLE_PERMISSIONS` map while `workspaces.py:add_member` kept its own `("owner", "admin")` tuple, so the map was dead code and the route enforced a different rule. The route now goes through the map and the matrix test fails if the two drift again. Approval logic has no second implementation yet | Code review; `tests/test_permission_matrix.py::test_declared_routes_match_the_live_app` |
| WARN-B-007 | MEDIUM | PREVENTIVE | Breaking API or schema changes without a path | API, DB | Client breakage | Version APIs; reversible migrations | Open | Contract tests |
| WARN-B-008 | LOW | PREVENTIVE | Circular dependencies between modules | Modules | Fragile builds | Keep dependency direction per master doc §15.8 | Resolved 2026-11-16: `vistaro/sentinel/` now has an `__init__.py`, and `api/deps.py` imports the sentinel map rather than duplicating it; import direction across `core -> db -> sentinel -> api` holds. `import-linter` reports 1 contract kept, 0 broken (the single existing contract only covers `core`) | `uv run lint-imports` |
| WARN-B-009 | HIGH | PREVENTIVE | RLS tenant setting applied at connection level instead of transaction level; with pooled connections one request can inherit another tenant's setting | Database access layer | Cross-tenant data exposure | Use transaction-local `set_config(..., true)` only; wrap every request and task in one transaction; isolation tests | Partially addressed: transaction-local behavior proven by `tests/test_tenancy.py::test_pooled_connection_reuse_does_not_leak_scope` (2026-10-24); session-GUC stays at `''` after commit, and the old policy cast errored instead of denying - fixed in migration `0002`. The control is transaction-scoped on the paths that use `tenant_session()` (all AUTH-002 routes); session lookups and the readiness probe run on connections that carry no tenant scope by design | `AUTH-002` request/task wrapper | Every request and task reuses `vistaro.db.tenancy.set_tenant_scope` in one transaction |
| WARN-B-014 | MEDIUM | PREVENTIVE | Redis rate limiter fails **closed**: when Redis is unavailable, every non-health route answers 503 | API availability | Redis is a hard dependency for availability | Decide the trade-off deliberately; at minimum record it in the ops runbooks (`OPS-001`) | Open — raised for the founders' confirmation 2026-10-27; never resolved | Failure-injection test with Redis down |
| WARN-B-015 | LOW | PREVENTIVE | `/readyz` builds and discards a throwaway engine (one new TCP connection) per call | Readiness probe | Connection churn; a slow Postgres makes readiness expensive | Pool the readiness probe's engine, or reuse the shared engine | Open — prep work had been assigned to `AUTH-002`, which is DONE and did not take it | Engine churn removed |
| WARN-B-010 | MEDIUM | PREVENTIVE | Celery misconfiguration (acks late, visibility timeout shorter than long steps, retries without idempotency) causes duplicate or lost steps | Agent runtime | Duplicate posts or messages, stalled goals | Idempotency keys, atomic claim, timeout longer than the longest step, reaper for stale tasks, DB as source of truth | Open | Failure-injection tests |
| WARN-B-011 | MEDIUM | PREVENTIVE | Own session-based authentication (ADR-007) carries implementation risk | Auth | Account takeover | Use vetted libraries (Argon2id, Authlib); `SEC-001` baseline; independent review in `SEC-002` | Partially addressed (2026-10-28): Phase A uses argon2-cffi only, digest-stored tokens, generic credentials errors with equalized timing. Residuals no row records: no independent security review yet (`SEC-002` is BACKLOG), no per-account login throttling (only the global 120/60s per-peer limit), no session rotation or revocation (absolute 7-day lifetime), and the OAuth `state` cookie uses the Starlette `SessionMiddleware` defaults rather than an explicit `same_site`/`https_only` | Auth tests; security review |
| WARN-B-012 | LOW | PREVENTIVE | `import-linter` contracts drift or are disabled, eroding module boundaries | Whole backend | Tangled modules | Run in CI; changes to contracts need review | Open | CI shows contracts enforced |
| WARN-B-013 | HIGH | OBSERVED | Database probes through libpq/psycopg can hang **indefinitely** when Postgres is unreachable; `/readyz` therefore never returned and any pooled engine built without a connect timeout blocked forever (found during the 2026-10-27 audit when Docker was down) | DB access layer, `/readyz`, tenancy tests | Readiness endpoint unreadable; test runs hang instead of failing fast | Engines must always set `connect_timeout` (`build_engine` does); new engine helpers must carry it | Resolved 2026-10-28: fix merged into `main` as `51f47b7`. The local branch `fix-readyz-connect-timeout` was never merged and is a stale duplicate; it was deleted 2026-11-16. Runtime re-check after the merge was not repeated — the evidence is the 2026-10-27 audit on the branch | Start Postgres, run `/readyz` (200), stop it, run again (503 within ~10s) |

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
| WARN-D-001 | CRITICAL | OBSERVED | Only `memberships` has row-level security; `workspaces`, `users` and `sessions` have none, and only `memberships` is in the isolation-test registry, so the generated isolation tests cover one table | All tenant tables | Cross-tenant data exposure if application scoping regresses | Server-derived scope on every query; row-level security on every table that carries tenant data; explicit, documented and tested exceptions where RLS does not apply | Open. Concrete state: RLS enabled and forced on `memberships` only (migration `0001`), policy extended in `0004`; `db/tenancy.py` registers only `memberships`; `tests/test_tenancy.py` covers only that table. `workspaces` carries `created_by` and the workspace name but no RLS and no registry entry — it needs a policy or a documented exception | `TEST-001` isolation tests for every tenant table |
| WARN-D-002 | HIGH | PREVENTIVE | Migrations without rollback or tested on unrealistic data | Database | Failed deploys, data loss | Reversible migrations; test on realistic copy | Open, but the evidence exists: all four migrations have `downgrade()`, and the `upgrade -> downgrade -1 -> upgrade head` cycle was verified on an seeded database (`CLAUDE.md` §12, DB-001). Not yet run against production-shaped data | Up and down test |
| WARN-D-003 | HIGH | PREVENTIVE | No backups or untested restores | Production DB | Unrecoverable loss | Daily backups; periodic restore test | Open. Local `infra/docker-compose.yml` holds a named volume only; no backup job or restore drill exists; `OPS-001` (runbooks and drills) is BACKLOG | Restore test recorded |
| WARN-D-004 | MEDIUM | PREVENTIVE | Audit logs modifiable or incomplete | Sentinel | Loss of accountability | Append-only; completeness tests | Open. No `audit_logs` table exists yet; `SEN-001` is `READY` but not started, and the roadmap still marks it `BLOCKED` | Audit completeness test |
| WARN-D-005 | MEDIUM | PREVENTIVE | Retention and deletion periods undefined | Conversations, contacts | Over-retention or accidental deletion | Define retention (`LEGAL-001`); deletion on request | Open | Retention policy recorded |
| WARN-D-006 | LOW | PREVENTIVE | Missing indexes on high-volume lookups (leads, messages, metrics) | Convert, Pulse | Slow queries | Add indexes from measured query plans, not guesses | Open | Query plan review |
| WARN-D-007 | MEDIUM | PREVENTIVE | The `sessions` table is looked up before a workspace is known, so it is not workspace-scoped by RLS | Auth | Session misuse if scoping by user is wrong | Scope by `user_id` in code; hash session IDs; document the exception; test it | Partially addressed (2026-11-01): sessions are resolved by digest only; every session write (last-seen refresh, CSRF rebind, workspace switch) is digest- or user-scoped, and the switch endpoint verifies live membership in the same transaction. Still open: `AUTH-001`, `AUTH-002` and `AUTH-003` all consume sessions and there is no session-scoping test — add one with the feature that next touches sessions | Session scoping tests |
| WARN-D-008 | LOW | PREVENTIVE | `audit_logs`, `agent_runs`, and metrics tables grow without bound | Database | Slow queries, cost | Retention policy; partitioning when measured need appears | Open | Size monitoring |
| WARN-D-009 | MEDIUM | PREVENTIVE | `add_member` answers 404 `USER_NOT_FOUND` for unknown emails, and signup answers 409 `EMAIL_ALREADY_IN_USE`: existing account existence is revealed to any signed-in caller | Account privacy | Account enumeration by any signed-in workspace admin / signup caller | Add an email-invite-token flow, or return a generic error for both cases; accept the documented trade-off until then. Both flows are deliberately public-facing and recorded in `CLAUDE.md` §12 | Accepted, documented — founders to confirm they want the invite-token flow instead (2026-11-16) | Invite-token flow instead of email lookup |
| WARN-D-010 | MEDIUM | PREVENTIVE | Every co-member can list every other member's email address — member emails are a shared collaboration surface | Member privacy | Unwarranted disclosure of staff's personal email addresses | Confirm the collaboration-surface intent with the founders, or return only names/roles for non-owners | Accepted, documented — founders to confirm (2026-11-16) | Founder decision on the member-list payload |

---

## E. Security and privacy warnings

| ID | Sev | Type | Description | Affected | Impact | Recommended control | Status | Verification required |
|---|---|---|---|---|---|---|---|---|
| WARN-E-001 | HIGH | PREVENTIVE | Integration tokens stolen or logged | Connectors | Account takeover on customers' channels | Encrypt at rest; least privilege; rotation; never log | Open | Log scan; token handling review |
| WARN-E-002 | HIGH | PREVENTIVE | Personal data of customers in logs, fixtures, prompts sent to providers, or docs | Logging, AI calls | Privacy breach | Redact; minimize what is sent to LLM providers; synthetic fixtures | Open | Log and fixture review |
| WARN-E-003 | MEDIUM | PREVENTIVE | Unvalidated input and file uploads (brand assets, lead forms) | API | Injection, malware, abuse | Validate and size-limit; scan uploads; rate limit | Partially addressed: global Redis rate limit (SEC-001) plus input validation on every implemented route (`extra="forbid"`, control-character and role whitelist, length limits). Still open: no file-upload path exists at all (no validation, scanning or size limit), no per-route rate limits, no form-abuse tests | Negative tests |
| WARN-E-004 | MEDIUM | PREVENTIVE | Third-party data sharing without consent or understanding | LLM and platform providers | Legal exposure | Document what data goes to which provider | Open | Data-flow doc |
| WARN-E-005 | MEDIUM | UNVERIFIED-DEPENDENCY | Applicability of India's data protection law and platform terms to Vistaro is not assessed (R-09) | Whole product | Compliance gaps | `LEGAL-001` | Open | Advisor input |
| WARN-E-006 | LOW | PREVENTIVE | Session and token handling weaknesses | Auth | Session hijack | Short-lived tokens; secure cookies; bind CSRF validation to the authenticated session | Addressed (2026-11-01): CSRF tokens are session-bound (`sessions.csrf_token_hash`) and each login mints a fresh session id; `GET /csrf` re-binds to a live session; every unsafe method is rejected with 403 `CSRF_VALIDATION_FAILED` unless both the cookie and the header hash to the stored digest, with tests in `tests/test_auth_api.py` and `tests/test_security.py`. Residual: absolute 7-day session lifetime, no rotation or revocation | Auth review |
| WARN-E-007 | HIGH | UNVERIFIED-DEPENDENCY | Rate-limit client identity behind the hosting proxy is not verified. SEC-001 keys limits on the direct ASGI peer and deliberately ignores forwarded headers | API deployment | Multiple users may share one proxy peer and hit the same limit; trusting spoofable forwarding headers could instead bypass limits | Keep direct-peer identification until the hosting proxy chain is documented and trusted-proxy handling is explicitly configured | Open; verify during `INFRA-001` before staging exposure | Confirmed proxy behavior and tested trusted-proxy configuration, if needed |
| WARN-E-008 | MEDIUM | UNVERIFIED-DEPENDENCY | Staging is a cross-site pair (Cloudflare Pages SPA calling a Render API). The API issues session/CSRF cookies with `SameSite=None; Secure` for every non-local environment (`core/security.py::session_cookie_options`/`csrf_cookie_options`), so cross-site cookies **do** ride along over HTTPS. The residual staging risks are narrower and threefold: `WEB_ORIGIN` must be the real Pages origin (CORS is credentialed and origin-scoped), `Secure` requires HTTPS (a plain-HTTP staging URL will 401 on cookie round-trips), and the Google sign-in `state` cookie is issued by Starlette `SessionMiddleware` with its library defaults (`same_site=lax`, `https_only=False`) rather than the API's own security defaults | Staging (INFRA-001/DEPLOY-001) | A misconfigured origin or non-HTTPS staging shows as "sign-in does not work" with no code defect to find | During `INFRA-001`: set the real Pages and API origins, serve both over HTTPS, verify a full sign-in from the staging origin, and set the OAuth session cookie attributes deliberately (`same_site`, `https_only`) alongside the session cookie options | Open; resolve with the staging topology decision | Sign-in verified end-to-end from the real staging origin |
| WARN-E-009 | MEDIUM | OBSERVED | Two user-facing auth gaps: the verification link in the sign-up email points at the API's JSON `GET /auth/verify`, so a user clicking it sees raw JSON, and the SPA route `/verify-email` handles it properly but the email does not point there; `/auth/me` does not expose `active_workspace_id`, so the workspace switcher cannot show which workspace is active after a reload | Auth, web | Confusing sign-up and switch experience | Point the email link at the SPA route with a 302; expose `active_workspace_id` on `/auth/me` (or the workspaces list) | Open — observed in the 2026-11-16 UI-001 live session; both are small changes, fold either into the next auth task or a standalone PR | Email link 302s into the SPA; switcher shows the active workspace after reload |

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
| WARN-F-007 | MEDIUM | UNVERIFIED-DEPENDENCY | Hosting plan, region, credits, and `pgvector` availability on Render are unverified | Infrastructure | Rework or cost surprise | Verify in `INFRA-001`; containers keep the move to another host cheap | Open. One mutable reference already shipped in local infra: `infra/docker-compose.yml` runs `axllent/mailpit:latest` and a floating `postgres:16` tag, the same mutable-ref class as `WARN-A-008`. Pin the local images to reviewed tags while in there | Findings recorded in `INFRA-001` |
| WARN-F-008 | LOW | PREVENTIVE | Single instance each of API, worker, and beat at launch means no high availability | Operations | Downtime during failures or deploys | Accept for MVP; backups and rollback rehearsal; scale per ARCHITECTURE §15 | Open. No Celery worker or beat exists yet, so there is no single-instance worker to fail today | Rollback rehearsal |

---

## G. Known bugs and technical debt

### G.1 Code defects

One observed defect has been recorded and verified; it no longer reproduces.

| ID | Sev | Type | Description and evidence | Affected | Impact | Workaround | Recommended fix | Status | Verification |
|---|---|---|---|---|---|---|---|---|---|
| WARN-B-013 | HIGH | OBSERVED | DB probes hang when Postgres is unreachable — see section B. Evidence: 2026-10-27 audit with Docker down | `/readyz`, tenancy tests | `/readyz` never returned; test runs hung | start Postgres | `connect_timeout=5` on every engine | Resolved 2026-10-28 (`51f47b7`) | Re-run `/readyz` with Postgres stopped |

Template for new findings:

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
| WARN-G-008 | MEDIUM | OBSERVED | **Documents were generated without a repository.** Every implementation statement is unverified; commands in the guide are targets. `REPO-000` (2026-10-23) confirmed the repository existed but contained documentation only; `REPO-001` created the bootstrap | All docs | Docs may not match reality once code exists | Run `REPO-000`; record verified commands | `REPO-000`, `REPO-001` | Partially resolved: bootstrap, API-001, SEC-001, DB-001, TEST-001, AUTH-001/002/003 (backend) and UI-001 (frontend) commands are all verified in `CLAUDE.md` §12/§12b. Still targets: staging, deploy, workers | Fresh-clone test; CI on a PR |
| WARN-G-009 | LOW | OBSERVED | **Documentation paths do not match the tree.** Docs linked to `/docs/*.md` and `docs/adr/`, but all markdown files were at the repository root on 2026-10-23 | All docs links; `REPO-001` layout | Broken references and confusion | Move docs into `docs/` during `REPO-001`, or update every link | `REPO-001` | Resolved 2026-10-23: reference docs moved to `docs/`; root keeps `CLAUDE.md`, `AGENTS.md`, `README.md`, `STARTUP_*`, and `Vistaro.docx` | Fresh-clone test; links resolve |
| WARN-G-010 | MEDIUM | OBSERVED | **Verification gaps from the bootstrap.** CI verified on PR #1; Postgres service, `alembic upgrade/downgrade/upgrade`, and RLS policy verified locally during DB-001 (2026-10-23). Still open: Redis and Postgres run in CI (postgres:16-alpine, redis:7-alpine, health checks), Mailpit is **not** in CI at all, `axllent/mailpit:latest` is a mutable tag in compose, and the staging half of `INFRA-001` (secrets in platform store, plan/region/`pgvector`) | `INFRA-001` | False sense of completion | Verify staging separately; keep local compose findings recorded in `CLAUDE.md` §12 | `INFRA-001` | Partially resolved | Staging reachable with secrets only in the platform store |

---

## Change log

| Date | Change |
|---|---|
| 2026-10-17 | Initial register created. No code defects recorded because no repository was inspected. Preventive controls clearly labeled. |
| 2026-10-18 | Updated for the decided stack: resolved or mitigated stack-related entries; added WARN-B-009 to B-012, C-009 to C-011, D-007, D-008, F-007, F-008, G-007, G-008. |
| 2026-10-23 | `REPO-000`: recorded the docs-only repository state; updated WARN-G-008 to partially addressed; added WARN-G-009 (docs paths versus actual root layout). |
| 2026-10-23 | `REPO-001`: created the bootstrap, moved reference docs into `docs/`, added CI and compose files, and verified a fresh clone; added WARN-G-010 for CI/compose verification gaps; updated WARN-B-004, WARN-G-008, WARN-G-009. |
| 2026-10-23 | PR #1 merged and CI green: closed the CI part of WARN-G-010; Docker Compose remains unverified locally. |
| 2026-10-23 | `DB-001`: Docker Desktop installed; Postgres service verified via compose and `alembic` upgrade/downgrade/upgrade verified on empty and seeded databases; RLS proven enforced for `vistaro_app`. Narrowed WARN-G-010 to the staging half of `INFRA-001`; noted WARN-B-009 control (transaction-local setting) is designed in but its harness is `TEST-001`. |
| 2026-10-24 | `TEST-001`: harness proves the WARN-B-009 control works (transaction-local scope does not survive commit) and caught a related defect: on pooled connections the session GUC stays at `''` after commit and the original policy cast errored instead of denying; migration `0002` replaces the policy with a `NULLIF` version. `TEST-001` sabotage check verified: dropping the policy makes three tests fail; restored, they pass. |
| 2026-10-24 | `SEC-001`: added tested CSRF double-submit and same-origin checks, secure cookie defaults, API security headers, Redis rate limiting, and dependency audits. Added WARN-E-007 for the unverified hosted proxy chain; no forwarded IP header is trusted. |
| 2026-10-24 | `SEC-001` review identified WARN-A-008: CI third-party actions use mutable refs, including TruffleHog `@main`; SHA pinning remains an open supply-chain hardening item. |
| 2026-10-27 | Independent audit of merged API-001/SEC-001: suites green and controls verified live; added WARN-B-013 (found and fixed locally: `build_engine` had no `connect_timeout`, so `/readyz` and test runs could hang forever with Postgres down). Noted for founders: the Redis rate limiter fails **closed** (503 for every non-health request when Redis is unavailable) — safer than fail-open, but it couples API availability to Redis; confirm this trade-off stands. |
| 2026-10-28 | Founders' request: no bot-authored commits. Removed `.github/dependabot.yml` and recorded that dependency bumps are manual (`uv lock` / `pnpm update`); Dependabot security **alerts** stay available in Settings. WARN-A-008 mitigation updated (SHA pinning is now a manual review item). | Claude (delegated) |
| 2026-10-28 | `WARN-B-013` fix merged into `main` as `51f47b7` ("bound DB connect timeout so /readyz fails fast instead of hanging"). The local `fix-readyz-connect-timeout` branch was never merged and is a stale duplicate; recorded here so the fix is traceable to its merge commit. | Claude (delegated) |
| 2026-11-01 | `AUTH-001` Phase A and Phase B merged (PRs #12/#13, #14); CI 4/4 on both merges. Decision-log noting "no bot-authored commits" applied after the fact: Dependabot PRs #6–#11 were merged on 2026-10-28, the same day the config was removed. Recorded in section A (WARN-A-008). | Claude (delegated) |
| 2026-11-02 | `AUTH-002` merged into `main` via PR #15: workspaces, switching, members; migration `0004` (memberships RLS user branch); `tenant_session` helper. 110/110 backend tests, CI 4/4; live smoke recorded in `CLAUDE.md` §12. | Claude (delegated) |
| 2026-11-16 | `UI-001` merged into `main` via PR #17: web app shell and router, auth screens, session guard, workspace switcher, loading/empty/error states, CSRF-refresh mutations, Playwright setup. 43 files, 2256 insertions. Vitest 27 green, Playwright E2E 3/3 against the real stack; E2E caught and fixed a StrictMode double-verify bug. | Claude (delegated) |
| 2026-11-16 | `AUTH-003` implemented and recorded: `vistaro/sentinel/permissions.py` (`ROLE_PERMISSIONS`, `has_permission`, `require`, `may_approve`, `PROTECTED_ROUTES` registry), `require_permission` dependency in `api/deps.py`, routes rewired, generated matrix test (`tests/test_permission_matrix.py`), `sentinel/__init__.py`. 132 backend tests green; ruff, mypy, lint-imports clean. WARN-B-001/B-006 updated; WARN-B-008 resolved. | Claude (delegated) |
| 2026-11-16 | Documentation audit across all records: WARN-A-001, WARN-A-006, WARN-A-008, WARN-B-002, WARN-B-004, WARN-B-011, WARN-B-014/015, WARN-D-001..010, WARN-E-003/E-006/E-008/E-009, WARN-F-007/F-008, WARN-G-008/G-010 updated to match the code and the current merges; the migration's stale WARN-C-003 pointer removed from `alembic/versions/0003_email_verification_and_session_csrf.py`. Added an index and summary to the top of this register. | Claude (delegated) |
