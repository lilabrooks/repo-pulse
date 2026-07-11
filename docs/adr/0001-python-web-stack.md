---
type: ADR
title: Python web stack
description: FastAPI + uvicorn backend, httpx client, pytest tests, hand-written static frontend.
tags: [stack, dependencies, python]
timestamp: 2026-07-09T00:00:00Z
owner: Lila Brooks
deciders: [Lila Brooks]
status: proposed
---

# Status

Proposed (authored by Claude Code per the decision policy; awaiting owner review)

# Context

Repo Pulse needs a Python backend that serves a JSON API and static files, an HTTP client for the GitHub REST API, and an offline test harness. `docs/GOAL.md` fixes Python 3.12+, a no-Node static frontend, and environment-only secrets, and delegates the framework, HTTP client, and test tooling choices to proposed ADRs. The development machine has Python 3.14 and PyPI access.

# Decision

Four pinned dependencies, installed into a project-local `.venv` driven by `make`:

- **FastAPI 0.139.0** — the web framework. Declarative routes, automatic request validation for the `owner`/`repo` path params, and a built-in static-files mount cover everything the goal needs.
- **uvicorn 0.51.0** — the ASGI server behind `make run`.
- **httpx 0.28.1** — the HTTP client for GitHub calls. Its `MockTransport` lets the test suite exercise the real client code path with zero network, which the goal's offline-test criterion requires. Also used by FastAPI's `TestClient`.
- **pytest 9.1.1** — test runner (dev dependency).

`requirements.txt` pins exact versions so clean installs are repeatable and Dependabot can propose explicit version bump pull requests.

The frontend stays hand-written HTML/CSS/JS under `static/`, served by the backend; no build step, per the goal constraints.

Alternatives considered:

- **Flask + requests**: equally capable, but mocking `requests` cleanly needs an extra library (`responses`) or monkeypatching, and path-param validation is manual. No advantage here.
- **Stdlib only (`http.server` + `urllib`)**: zero dependencies, but hand-rolled routing, JSON handling, and test plumbing bloat exactly the code this app should keep small. Rejected for verbosity, kept as the fallback if dependency weight ever becomes a problem.

# Consequences

Four runtime/dev dependencies to keep current; `requirements.txt` is the single pinned manifest. Tests and the app share the httpx client abstraction, so GitHub API behavior is testable offline. Dependabot version updates should be reviewed as ordinary dependency changes and verified with the offline suite. Rollback trigger: if the dependency surface causes install or maintenance pain, collapse to the stdlib fallback — the API contract in `docs/specs/api.md` is framework-neutral, so the swap stays contained.
