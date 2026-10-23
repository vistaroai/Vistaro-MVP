# CLAUDE.md — Vistaro AI Development Control File

> Mandatory instructions for every AI coding agent working on **Vistaro**.
> Read this file completely before touching any code. Last updated: 2026-10-22 (stack finalized: free and open source only).

## 0. What this file is (and is not)

This file controls **how** you work: workflow, safety rules, verification, reporting.
It does not describe the whole product. Product knowledge lives in the files below. Read them; do not guess.

### File hierarchy (one source of truth per topic)

| File | Role | Path |
|---|---|---|
| `CLAUDE.md` | Rules and mandatory workflow | `/CLAUDE.md` |
| `docs/ARCHITECTURE.md` | **Authority for the tech stack, structure, licence policy and design (v1.1, final)** | `/docs/ARCHITECTURE.md` |
| `docs/DEVELOPMENT_GUIDE.md` | Build how-to (setup and workflow) | `/docs/DEVELOPMENT_GUIDE.md` |
| `docs/adr/` | One file per approved change to an architecture decision | `/docs/adr/` |
| `docs/PROJECT_ROADMAP.md` | Complete phased roadmap, all tasks | `/docs/PROJECT_ROADMAP.md` |
| `docs/ACTIVE_TASKS.md` | Current execution queue | `/docs/ACTIVE_TASKS.md` |
| `docs/PROJECT_WARNINGS.md` | Warnings, risks, known bugs, technical debt | `/docs/PROJECT_WARNINGS.md` |
| `STARTUP_AI_MASTER_CONTEXT.md` | Full AI-oriented product and technical knowledge | repo root (intended path) |
| `STARTUP_MASTER_BLUEPRINT.md` | Human-oriented business and engineering rationale | repo root (intended path) |

Do not create duplicate or competing copies of these. If an equivalent file already exists in the repository, inspect and update it.

### Compatibility with `AGENTS.md`

If the repository uses `AGENTS.md` for shared agent instructions, keep it as a thin pointer to this file (see `AGENTS.md` in the delivery set). Do not maintain two divergent rule sets. If nested `CLAUDE.md` or `AGENTS.md` files exist in subfolders, read the ones relevant to the files you change; shared rules stay here.

### Status of the project at the time this file was written (verify before trusting)

- Vistaro is at the **idea / pre-build stage**. At creation time **no repository, code, tests, or deployment were visible** to the author of this file. Every statement about implementation in these docs is therefore **UNVERIFIED** until you inspect the repository.
- No feature is marked `DONE`. **The technology stack and hosting are decided** (`docs/ARCHITECTURE.md` v1.1, `DEC-001` done): everything Vistaro runs must be **free and open source**. Still open: which open-weight LLM (`DEC-002`), VM provider and domain (`DEC-005`), backup destination (`DEC-006`), pricing and first customer niche.
- If the repository now contains code, **the repository is the evidence of what exists**. Update the roadmap to match it (see §12).

---

## 1. Mandatory startup procedure

Run this sequence at the start of every session. Keep it proportional: for a one-line low-risk fix, steps 2 to 4 can be a few sentences.

### Step 1: Understand the project
1. Read this file.
2. Read `docs/ARCHITECTURE.md` (stack, structure, licence policy), then `STARTUP_AI_MASTER_CONTEXT.md` (product, decisions, constraints, open questions). If the master document's stack suggestion differs from `ARCHITECTURE.md`, `ARCHITECTURE.md` wins.
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
1. Read `docs/ACTIVE_TASKS.md`, then the relevant entries in `docs/PROJECT_ROADMAP.md`.
2. Check dependencies, priority, blockers, acceptance criteria.
3. Choose the highest-priority **READY** task appropriate to the request.
4. If the user asks for a different task, do that task, unless it conflicts with a critical safety rule or a documented dependency. If it does, explain and propose a safe path.
5. Do not start unrelated features because they seem useful.
6. If the next task is unclear, or a decision materially affects architecture, security, data integrity, or business direction, explain the uncertainty and ask.

### Step 4: Plan before substantial changes
State briefly: objective; affected files and components; approach; dependencies, risks, regressions; tests and acceptance criteria. Check `docs/PROJECT_WARNINGS.md` first (§7). Prefer the smallest reliable implementation.

### Step 5: Implement safely
- Follow existing architecture and conventions. Reuse existing components and patterns.
- No duplicate functionality, no unnecessary dependencies. **Check the licence of every new dependency, image and model against rule 19 before adding it.**
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
  - **Free and open source only (founder instruction, 2026-10-22).** Everything Vistaro runs or links into its code must be free and open source (policy: `ARCHITECTURE.md` §0). Free-to-use external services (Google sign-in, Meta, Razorpay, an SMTP relay, GitHub) are allowed only as optional or replaceable integrations.
- **Stack in one line (authority: `ARCHITECTURE.md`):** modular monolith; Python/FastAPI backend; React/TypeScript/Vite frontend; PostgreSQL with RLS and pgvector; Celery + Valkey; self-hosted open-weight LLM behind an OpenAI-compatible interface (Ollama, later vLLM); Docker Compose on a free VM behind Caddy; GlitchTip, Uptime Kuma, restic, SOPS + age.
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
18. **Secrets:** use SOPS-encrypted files or restricted environment files; never commit plaintext secrets or the age private key. Provide `.env.example` with placeholder names only.
19. **Free and open source only.** Do not add a dependency, container image, model, font or service whose licence is not on the allow-list in `ARCHITECTURE.md` §0 (no source-available or non-commercial licences; GPL/AGPL only for standalone services we run unmodified). The CI licence check must pass. If something good seems to need an exception, stop and propose an ADR; do not add it.
20. **Self-hosted LLM honesty.** When the LLM server is slow, down or returns invalid output, the step retries within its cap and then fails visibly. Never return canned, mocked or invented output in its place. Do not expose the LLM server, database or Valkey to the internet.
21. **Backups before risk.** Take and verify a backup before any production migration or destructive operation. We host the data ourselves; there is no provider safety net.

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

**Approval flag in the roadmap:** `APPROVED-SCOPE` means the capability is part of the founders' confirmed spec. `PROPOSED-TASK` means the specific task breakdown was drafted by an AI and has **not** been approved. Do not treat a proposed task as approved scope without the founders' acceptance.

---

## 6. Hierarchy of truth

1. Explicit, current instructions from the user for the current task (subject to safety rules).
2. Actual repository state, for what has been implemented.
3. Approved architecture decisions (`docs/ARCHITECTURE.md` and `docs/adr/`) and current product requirements.
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
- LLM server reachability and model loaded (internal network only), latency on a small fixed prompt.
- Backups: last successful backup time and last restore test.
- Licence check result.
- Background jobs and scheduled tasks.
- Authentication and authorization behavior.
- Error logs and known warnings.
- Deployment configuration.

Report a concise health summary that separates **verified findings** from **checks not performed**. Not every check applies to every project.

---

## 9. Architectural change approval

Needs a written proposal **before** implementation: switching databases; replacing the frontend or backend framework; changing the auth strategy; adopting a major AI orchestration framework; changing a core API contract; reorganizing major modules; adding expensive infrastructure; changing how sensitive data is stored or processed.

The proposal states: current design; proposed change; why necessary; alternatives considered; migration and compatibility risks; implementation and test plan. After approval, add a file under `docs/adr/` and update `docs/ARCHITECTURE.md`. Any change that introduces a component outside the licence allow-list (rule 19) also needs this process.
Small internal refactors do not need this process. Keep it proportional to risk.

**Decided (do not re-open without an ADR):** the stack in `docs/ARCHITECTURE.md` v1.1, summarized in §2. Decision `DEC-001` is recorded as done in the roadmap (Dimple signed off on 2026-10-22; Anushka Varshney's acknowledgment is pending, and either founder may veto).

**Still open (propose, do not assume):**

| Item | Task | Note |
|---|---|---|
| Which open-weight model(s) and quantization | `DEC-002` | Evaluate on a fixed task set; check the model's licence |
| VM provider, region, domain | `DEC-005` | Oracle Cloud Always Free is the candidate; verify terms |
| Off-VM backup destination | `DEC-006` | Must not be the same VM |
| Embedding model | Phase 3 | ADR-020 |
| Razorpay and WhatsApp use | Phase 2 / 4 | Not free to use; may be dropped under the free-only rule |

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

## 12. First session in a repository that already has code

If code exists and the roadmap says otherwise:
1. Inspect the repository (§1 Step 1 and 2).
2. Record what exists in `docs/PROJECT_ROADMAP.md`, using status `IN_REVIEW` (implemented but not verified) rather than `DONE` until acceptance criteria are checked.
3. Replace the "no repository inspected" notes in these docs with verified facts.
4. Record real commands in a "Verified commands" section below.
5. Ask the founders to confirm anything that looks like an unapproved architectural choice.

### Verified commands (fill in only after discovery; do not guess)

Intended tooling from `ARCHITECTURE.md` (**not verified**; discover the real commands once the repository exists): `uv`, Ruff, mypy, pytest, Alembic on the backend; Vite, Vitest, Playwright on the frontend; `docker compose` for local and deployed stacks; `import-linter` and the licence check in CI.

| Purpose | Command | Verified on | Notes |
|---|---|---|---|
| Install | UNKNOWN | | |
| Run dev | UNKNOWN | | |
| Test | UNKNOWN | | |
| Lint | UNKNOWN | | |
| Type-check | UNKNOWN | | |
| Build | UNKNOWN | | |
| Migrate DB | UNKNOWN | | |

---

## 13. Keeping this file small

This file holds rules and workflow only. If it grows, split detail into focused files under `docs/` and link them here. Avoid circular references and duplicated policies. For multi-app repositories, add local `CLAUDE.md` files per app and keep shared rules here.
