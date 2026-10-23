# AGENTS.md — Vistaro

This file exists for tools that read `AGENTS.md`. **The rules live in `/CLAUDE.md`. Read it first and follow it completely.** Do not maintain a second rule set here.

Reading order:
1. `/CLAUDE.md` (mandatory workflow and rules)
2. `/docs/ACTIVE_TASKS.md` (what to do now)
3. `/docs/PROJECT_ROADMAP.md` (full plan and acceptance criteria)
4. `/docs/PROJECT_WARNINGS.md` (check before changing a component)
5. `/docs/ARCHITECTURE.md` (final design) and `/docs/DEVELOPMENT_GUIDE.md` (how to build)
6. `/STARTUP_AI_MASTER_CONTEXT.md` and `/STARTUP_MASTER_BLUEPRINT.md` (product context)

Essentials, repeated for safety:
- Inspect the real repository before changing anything; docs may be out of date.
- Never claim a test passed unless you ran it.
- Never bypass Sentinel approvals or workspace isolation.
- Never commit secrets; never run destructive commands or deploy without the founders' approval.
- Keep diffs small and explain them; the founders prefer to validate their own code.
- End every session with the report format in `CLAUDE.md` §11.
