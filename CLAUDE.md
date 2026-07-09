---
type: Playbook
title: Claude Code repo instructions
description: Master objective, grounding rules, and workflow for Claude Code in this repository.
tags: [claude-code, agent-instructions, adr, specs]
timestamp: 2026-07-09T00:00:00Z
owner: Lila Brooks
deciders: [Lila Brooks]
---

# Master objective

Current state: Freshly installed OKF workflow repo; no application code yet. Repo Pulse is being built here: a local web dashboard for the health of public GitHub repositories.

Target state: A Python backend serving a JSON API (`/api/health`, `/api/repo/{owner}/{repo}`) plus a static HTML/CSS/JS dashboard, consuming the GitHub REST API v3 with mocked-offline tests, an in-memory TTL cache, and optional `GITHUB_TOKEN` from the environment.

Constraints: Follow `docs/GOAL.md` and the specs in `docs/specs/` (API contract in `docs/specs/api.md` once it lands) and all accepted ADRs in `docs/adr/`. Python 3.12+, no Node toolchain, no database, secrets only via environment.

Done when: `make test` passes offline, `make run` serves the dashboard on `localhost:8000`, every milestone in `docs/GOAL.md` is checked with its verification, and `git check-ignore .env` succeeds.

# Preloaded context

These imports resolve when Claude Code loads this file, so the goal and the knowledge indexes are in context at session start without a read step. Keep the imported files small; full specs and ADRs stay on disk until a task needs them.

@docs/GOAL.md
@docs/specs/index.md
@docs/adr/index.md

# Goal iteration

`docs/GOAL.md` defines what this repo is for: the kind of deliverable (app, service, or utility), the problem, the target state, success criteria, and an ordered milestone backlog. The Master objective above is its one-screen summary; keep the two consistent, with `docs/GOAL.md` carrying the detail.

- `docs/GOAL.md` is preloaded by the import above, so the goal is in context from the first task. Re-read it during a session only after it changes.
- When asked to continue or iterate without a specific task, take the first unchecked milestone and run it through the task workflow below. When its verification passes, check it off, log it, and continue with the next unchecked milestone. Stop when the backlog is empty, a decision reserved for me comes up, or I say stop.
- Resuming after an interruption: at session start, if the working tree holds uncommitted changes, treat them as in-flight work from a cut-off session, not a clean slate. Reconcile them against the first unchecked milestone and the newest `docs/log.md` entry, then finish that work or back it out before taking a new milestone.
- Check a milestone off only when its stated verification passes, then add a dated `docs/log.md` entry.
- When every milestone is checked and the success criteria pass, report that the goal is met and stop. Don't invent new milestones; adding scope is my decision.
- When the code and the goal disagree, flag it. Changing `docs/GOAL.md` (scope, success criteria, milestone order) is my decision.
- If `docs/GOAL.md` is missing, create it with these sections before the first milestone task: Goal (kind, problem, solution), Target state, Success criteria, Non-goals, Constraints, Milestones. If it, or this file, is missing content or still contains unfilled template brackets, run the goal interview below before iterating.

# Goal interview

When `docs/GOAL.md` or this file still needs filling, gather what's missing as a short interview with me — a few questions at a time, drafting as you go — instead of asking me to edit templates. Ask for, in order:

1. What I'm building and for whom → Kind and Problem. Example: a CLI that turns Figma exports into design tokens, for the frontend team → Kind: utility.
2. What exists when it's done, concretely → Target state. Example: `tokens build` converts every Figma export in the fixtures folder into JSON and CSS variables.
3. The mechanical verification — the test command and observable checks → Success criteria and Verification commands. Example: `npm test` passes, and the CLI run on fixture A reproduces its golden output exactly.
4. What this repo deliberately won't do → Non-goals. Example: no GUI, no Sketch support, no design-tool plugins.
5. Which stack, platform, and dependency choices are fixed up front, and which you may decide later through proposed ADRs → Constraints. Example: Node 20 is fixed; the token-storage format is yours to decide via a proposed ADR.
6. The first shippable slice and how to check it → the first milestone. Example: parse one fixture and emit JSON, verified by the parser test suite passing.

Push back on answers that can't be checked mechanically — "migrate the API to GraphQL" is a direction, not a done state; keep asking until each answer would let you verify progress yourself. Draft the remaining milestones from my answers and confirm the finished `docs/GOAL.md` with me before starting the loop. In an existing codebase, propose answers from the code first — detected test commands, structure, conventions — and let me correct them rather than asking cold. Manual editing stays a valid alternative; never overwrite goal content I wrote by hand.

# Docs bootstrap

If `/docs/specs` or `/docs/adr` doesn't exist yet, create this structure before the first task. Until these files exist, the Preloaded context imports above won't resolve; creating the structure fixes that from the next session on:

Installer note: when setting up a repo from outside Claude Code, prefer `bash scripts/create-new-repo <target>` for empty repos or `bash scripts/update-existing-repo <target>` for existing repos. This bootstrap section is the in-session fallback when those scripts were not used.

```
docs/
├── index.md        # bundle root: declares okf_version, links the bundle files
├── GOAL.md         # goal, success criteria, milestone backlog (see Goal iteration)
├── log.md          # dated changelog, newest first
├── okf-map.yml     # maps source paths to governing specs/ADRs
├── specs/
│   ├── index.md    # lists each spec with a one-line description
│   └── _drafts/    # generated spec drafts; review before promoting
└── adr/
    └── index.md    # lists each ADR with a one-line description
```

`docs/index.md` starts with a frontmatter block declaring the OKF version (the bundle root is the only `index.md` allowed frontmatter):

```yaml
---
okf_version: "0.1"
---
```

Every new spec or ADR file gets YAML frontmatter with at least a `type:` field (OKF v0.1), plus `title` and `description`. Keep each `index.md` current when files are added or renamed.

`docs/okf-map.yml` maps source globs to the specs and ADRs that govern them. Keep it current when modules move or new source areas get their own contracts.

# Agent config (committed to the repo)

- `.claude/settings.json` — shared project settings, including the Stop hook that enforces docs sync. Committed.
- `.claude/hooks/check-docs-sync.sh` — Stop hook, invoked via `bash` so no executable bit is needed. Committed. Don't move, rename, or disable it; if it blocks a stop, do the doc update it asks for.
- `.claude/hooks/check-okf-version.sh` — SessionStart hook, invoked via `bash`. Committed. Reports OKF spec version drift; act per the OKF version policy above.
- `scripts/okf` — repo-local OKF helper command. Committed. Use it for stale mapping checks, spec drafts, and ADR suggestions.
- `docs/okf-map.yml` — source-to-knowledge mapping used by `scripts/okf check-stale`. Committed.
- `.claude/settings.local.json` — personal overrides only. Never commit it.
- `CLAUDE.local.md` — personal per-repo memory. Never commit it.

During bootstrap, ensure `.gitignore` contains these 3 entries (the same set the installers append and `verify-install` requires):

```
.claude/settings.local.json
CLAUDE.local.md
.okf-kit-backups/
```

Everything else agent-related is committed: `CLAUDE.md`, `.claude/settings.json`, `.claude/hooks/`, `scripts/okf`, and all of `/docs`.

# OKF version policy

A SessionStart hook compares `okf_version` in `docs/index.md` against the latest spec version on the official OKF repo. When it reports drift:

1. Read the current spec at https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/SPEC.md and identify what changed.
2. Minor bump (e.g. 0.1 → 0.2): backward-compatible. Migrate automatically, before the first task of the session: update `okf_version` in `docs/index.md`, apply any new formatting or structural conventions across `/docs`, log the migration in `/docs/log.md`. No approval needed.
3. Major bump (e.g. 0.x → 1.0): may contain breaking changes. Stop and present me a migration summary before changing any `/docs` files.

Never modify spec or ADR content as part of a version migration; only formatting, frontmatter, and structure.

# OKF helper commands

`scripts/okf` is a repo-local Bash helper installed by this kit. It is not an official OKF CLI, not a global command, and not a prompt. Always run it with `bash scripts/okf ...` unless this repo intentionally wraps it another way.

- `bash scripts/okf check-stale` — run after changing source files. If it reports stale mappings, update the mapped spec/ADR or add a dated `/docs/log.md` rationale explaining why no knowledge file changed.
- `bash scripts/okf draft [paths...]` — generate fact-based drafts under `/docs/specs/_drafts/`. Treat drafts as scaffolding: verify them, rewrite them into human-readable commitments, then move promoted specs into `/docs/specs/` and update `/docs/specs/index.md`.
- `bash scripts/okf adr-suggest` — run when a change may include an architecture decision. Create a new ADR only when the suggestion points to a real decision: dependency, persistence, cache/queue/worker, auth/security/privacy, API contract, deployment, or ownership boundary.

# Grounding rules (docs are the source of truth)

- The spec and ADR indexes are preloaded by the imports above. Before planning any change, read the specific spec or ADR governing the files you'll touch.
- When code and docs disagree, flag the mismatch. Don't silently pick a side.
- If a task conflicts with an accepted ADR, stop and ask before writing code. Superseding an accepted ADR is my decision, made via a new ADR file.
- Architectural changes start with a new ADR in `/docs/adr/`, written per the decision policy below, before any implementation.

# Decision policy (I own the goal, you drive the decisions)

I provide the goal, constraints, and guardrails; you make the decisions that reach the goal and record them where I can review them.

- Implementation choices that stay inside existing specs, accepted ADRs, and the guardrails below are yours to make without asking.
- Decision-shaped changes — dependency, persistence, cache/queue/worker, auth/security/privacy, API contract, deployment, ownership boundary — start with a new ADR marked `status: proposed` in its frontmatter, covering context, decision, alternatives considered, consequences, and a rollback or revisit trigger. Implement against the proposed ADR, then flag it in your summary and in `docs/log.md`; I accept it, ask for changes, or revert.
- Reserved for me: changing `docs/GOAL.md`, superseding or contradicting an accepted ADR, and the actions the guardrails below mark as needing my go-ahead. When work can't proceed without one of these, record the blocker in `docs/log.md` and ask instead of working around it.

# Guardrails (hold in every session)

Tests and verification:

- Run the repo's test command (see Verification commands) after every change and before checking off any milestone. A milestone with failing tests is not done.
- Never delete, skip, weaken, or mark as flaky a failing test or check to get a green run. Fix the code; if the test itself is wrong, say so and get my confirmation before changing it.
- Report outcomes as they are. Failures, partial progress, and skipped verifications go in the summary and `docs/log.md`, not under the rug.

Security:

- Never write secrets — API keys, tokens, passwords, private keys, connection strings — into tracked files. Read them from the environment, and before creating an env or credentials file, confirm `.gitignore` covers it.
- Treat changes touching auth, sessions, input parsing, file paths, network exposure, crypto, or permissions as security-sensitive: validate input at trust boundaries, use parameterized queries, grant least privilege, and run `bash scripts/okf adr-suggest`; when it flags the change, record the decision as a proposed ADR.
- New runtime dependencies are decision-shaped: the proposed ADR names the alternatives considered and the maintenance and security tradeoff.

Needs my explicit go-ahead, every time:

- Force pushes or history rewrites on shared branches; deleting or migrating stored data; deleting files beyond the task's scope.
- Publishing, deploying, releasing, or calling external services with side effects.

# Workflow for each task

1. Impact analysis: name the specs and ADRs that govern the target files.
2. Implement. Run `make test` and make it pass.
3. Knowledge alignment: run `bash scripts/okf check-stale` when available. If behavior or a contract changed, update the governing spec or ADR to match, and add a dated entry to `/docs/log.md`, newest first (ISO `YYYY-MM-DD` headings). If no doc change is warranted, add a one-line entry to `/docs/log.md` saying why. New spec or ADR files also get added to their directory's `index.md`.
4. ADR check: run `bash scripts/okf adr-suggest` for dependency, persistence, cache/queue/worker, auth/security/privacy, public API, deployment, or ownership-boundary changes. Draft an ADR only for a real decision.

# Verification commands

- Tests: `make test` (pytest via the project venv; fully offline, GitHub API mocked)
- Lint/typecheck: `.venv/bin/python -m compileall -q app tests`
- Run locally: `make run` (serves `http://localhost:8000`)
- OKF stale map: `bash scripts/okf check-stale`
