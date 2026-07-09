---
type: Spec
title: Repo Pulse frontend
description: Behavior contract for the static dashboard served at /.
tags: [frontend, dashboard, static]
timestamp: 2026-07-09T00:00:00Z
owner: Lila Brooks
deciders: [Lila Brooks]
---

# Purpose

The dashboard is hand-written static HTML/CSS/JS under `static/`, served by the backend. No build step, no Node toolchain, no external assets. It consumes only the API in `docs/specs/api.md`.

# Behavior

- A single form accepts `owner/repo` (validated client-side as two non-empty segments) and fetches `GET /api/repo/{owner}/{repo}` with both segments URL-encoded.
- States: idle (form only), loading (status line), error (API `detail` message shown verbatim; network failure shows a "backend not running" hint), rendered (dashboard visible).
- Rendered view: a pulse banner colored by verdict (`active` green, `quiet` amber, `dormant` red, `archived` gray) with the verdict reasons, stat cards (stars, forks, watchers, open issues, open PRs, commits in 30 days, latest release or "none", license or "none detected"), and a link to the repository on GitHub.
- Dark and light color schemes follow `prefers-color-scheme`.

# Verification

- Automated: backend tests assert `/` serves the form and script hooks, and that `/static/app.js` and `/static/style.css` respond 200 (`make test`).
- Manual: JavaScript behavior has no automated harness (no Node toolchain, per goal constraints). The check is: `make run`, open `http://localhost:8000`, query a real repository, and confirm the rendered states — recorded in `docs/log.md` when performed.
