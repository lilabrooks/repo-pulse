---
type: Spec
title: Repo Pulse API
description: JSON API contract served by the Repo Pulse backend.
tags: [api, contract, backend]
timestamp: 2026-07-09T00:00:00Z
owner: Lila Brooks
deciders: [Lila Brooks]
---

# Purpose

The backend exposes a small JSON API consumed by the static dashboard. This spec is the contract; the frontend and tests depend on it.

# Endpoints

## GET /api/health

Liveness check. Always returns HTTP 200 with:

```json
{"status": "ok"}
```

## GET /api/repo/{owner}/{repo}

Fetches the repository from the GitHub REST API v3 and returns a normalized summary:

```json
{
  "repo": {
    "full_name": "octo/hello",
    "description": "A test repository",
    "html_url": "https://github.com/octo/hello",
    "stars": 420,
    "forks": 55,
    "watchers": 17,
    "archived": false,
    "license": "MIT"
  },
  "issues": {"open_issues": 8, "open_prs": 4},
  "release": {"tag": "v1.2.3", "name": "One point two three", "published_at": "2026-06-30T12:00:00Z"},
  "activity": {"commits_last_30d": 3, "last_push": "2026-07-07T09:00:00Z"},
  "pulse": {"verdict": "active", "reasons": ["last push 2 day(s) ago", "3 commit(s) in the last 30 days"]}
}
```

Contract notes:

- `watchers` is GitHub's `subscribers_count` (true watchers, not stargazers).
- GitHub's `open_issues_count` includes PRs; `open_issues` here subtracts open PRs (floor 0). Open PRs are counted with the `per_page=1` Link-header technique, not the search API.
- `release` is `null` when the repository has no releases.
- `commits_last_30d` counts commits on the default branch in the last 30 days, capped at 100; empty repositories count 0.
- `pulse.verdict` is one of `active` (push within 7 days), `quiet` (within 90), `dormant` (older or never), `archived` (overrides all).

Errors:

- Unknown or private repository -> HTTP 404, `{"detail": "repository not found"}`.
- GitHub rate limit exhausted -> HTTP 503 with guidance naming `GITHUB_TOKEN`.

## GET /

Serves the dashboard `static/index.html`. Static assets are mounted under `/static/`.

# Caching and rate limits

Successful summaries are cached in process memory for 300 seconds per `owner/repo` (ADR 0002), so repeated queries cost zero GitHub calls and responses may be up to 5 minutes stale. Errors are never cached. An optional `GITHUB_TOKEN` environment variable (see `.env.example`) raises the upstream rate limit; it is attached as a Bearer header and must never appear in tracked files.

# Testability

All GitHub access flows through `app.github.make_client()`, so tests inject an `httpx.MockTransport` and the suite runs with no network.
