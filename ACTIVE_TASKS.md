# ACTIVE TASKS — Vistaro

Concise execution queue. Details live in `/docs/PROJECT_ROADMAP.md`; do not duplicate them here. Rules: `/CLAUDE.md`.
Last updated: 2026-10-18 · Cycle: **Cycle 0 — Bootstrap and validation**

> Status words match the roadmap. If this file and the roadmap disagree, the roadmap wins; fix this file.

## Current task

| ID | Task | Status | Owner | Why now |
|---|---|---|---|---|
| REPO-000 | Locate and inspect any existing repository; record real structure and commands (or record that none exists) | READY | Anushka (platform) with an AI agent | Everything else depends on knowing the real starting point |

## Next actionable tasks (in order)

| # | ID | Task | Depends on | Status | Notes |
|---|---|---|---|---|---|
| 1 | REPO-001 | Create monorepo, CI, `.env.example`, README with verified commands | REPO-000 | READY | First coding task. Follow `DEVELOPMENT_GUIDE.md` §2 |
| 2 | DB-001 | Roles, extensions, base schema, RLS | REPO-001 | BLOCKED (until REPO-001 is DONE) | Write the tenancy test next (`TEST-001`) |
| 3 | TEST-001 | Cross-workspace isolation test harness | DB-001 | BLOCKED | Must exist before feature code |
| 4 | AUTH-001 | Signup, login, sessions, email verification | DB-001, SEC-001 | BLOCKED | |
| 5 | INFRA-001 | Local docker-compose and staging; verify hosting plan and `pgvector` | REPO-001 | BLOCKED | Can run in parallel with DB-001 once the repo exists |

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
| No repository confirmed | All build tasks | REPO-000 |
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
| 2026-10-18 | `DEC-001` stack and architecture | Decided under founders' delegation; see `ARCHITECTURE.md` |
| 2026-10-18 | `DEC-003` minimal approval in Phase 1 | Yes |
| 2026-10-18 | `DEC-004` competitor watch in Pulse | Yes |

No software task is complete. **Do not mark any build task done without verification** (`CLAUDE.md` §4).

## Next recommended action

Run `REPO-000`, then `REPO-001`. Start `VAL-001` and `DOC-001` the same week.

## How to update this file

At the end of every session: move finished work to "Recently completed" (keep the last ~10), promote the next READY tasks, refresh blockers and awaiting-decision lists, and set the date. Keep it under about one page.
