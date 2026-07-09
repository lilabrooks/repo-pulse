---
type: Goal
title: Repo Pulse goal
description: A local web dashboard that shows the health of any public GitHub repository.
tags: [goal, milestones, dashboard, github]
timestamp: 2026-07-09T00:00:00Z
owner: Lila Brooks
deciders: [Lila Brooks]
---

# Goal

Kind: app

Problem: Developers evaluating a dependency or an open-source project have to click through half a dozen GitHub tabs (stars, issues, pull requests, releases, commit history) to judge whether it is alive and maintained.

Solution: Repo Pulse — a small local web app: a Python backend that consumes the GitHub REST API and serves a single-page dashboard where you enter `owner/repo` and get the repository's vital signs and a computed pulse verdict.

# Target state

- A Python backend exposing a JSON API: `GET /api/health` and `GET /api/repo/{owner}/{repo}` returning a normalized repository summary (repo facts, open issues vs open PRs, latest release, recent commit activity, pulse verdict).
- A static frontend (HTML/CSS/JS, served by the backend) with a repo input form and dashboard cards rendering that summary, including loading and error states.
- GitHub API consumption that is rate-limit friendly: responses cached in memory with a TTL, optional `GITHUB_TOKEN` read from the environment for higher limits.
- A test suite that runs fully offline: every GitHub API interaction mocked.

# Success criteria

- `make test` passes (pytest, no network required).
- `make run` serves the dashboard at `http://localhost:8000`; `curl http://localhost:8000/api/health` returns `{"status":"ok"}`.
- `GET /api/repo/{owner}/{repo}` returns the JSON shape documented in `docs/specs/api.md`; unknown repos return 404 with a clear message; GitHub rate limiting maps to 503 with guidance.
- No secrets in tracked files; `.env` is git-ignored and `git check-ignore .env` passes.

# Non-goals

- No database or persistence beyond the in-memory cache.
- No user accounts, login, or multi-user features.
- No deployment or hosting automation; this runs locally.
- No private-repo support and no GitHub write operations.
- No Node/frontend build toolchain; the frontend stays hand-written static files.

# Constraints

- Python 3.12+; frontend is static HTML/CSS/JS served by the backend.
- External data comes from the GitHub REST API v3 only.
- `GITHUB_TOKEN` is optional and read from the environment only; never tracked.
- Web framework, HTTP client, cache design, and test tooling are Claude Code's decisions via proposed ADRs in `docs/adr/`.
- Specs in `docs/specs/` govern the API and frontend contracts as they land.

# Milestones

Ordered backlog. When asked to continue without a specific task, Claude Code
takes the first unchecked milestone. Check a milestone off only when its
verification passes, and record progress in `docs/log.md`.

- [x] Skeleton: backend app serving `/api/health` and the static index shell, with test harness and Makefile (`make test`, `make run`). Verify: `make test` passes and a live `curl /api/health` returns `{"status":"ok"}`.
- [x] GitHub summary API: `GET /api/repo/{owner}/{repo}` returns the normalized summary per `docs/specs/api.md`; 404 and rate-limit errors mapped; tests fully mocked. Verify: `make test`.
- [x] Frontend dashboard: form plus pulse cards rendering the summary with loading and error states, served from `/`. Verify: `make test`; index page and static assets respond 200 and the dashboard renders against the live API in a manual browser check.
- [x] Rate-limit friendliness: in-memory TTL cache on repo summaries and optional `GITHUB_TOKEN` from the environment with a committed `.env.example` (cache decision via proposed ADR). Verify: `make test` cache tests pass and `git check-ignore .env` succeeds.
- [x] Polish: README quickstart (clean-clone to running dashboard), pulse verdict edge cases (no releases, empty repos, archived repos). Verify: `make test`; README steps reproduce on a clean checkout.
