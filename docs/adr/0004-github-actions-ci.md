---
type: ADR
title: GitHub Actions CI
description: Run the offline test, compile, and OKF mapping checks in GitHub Actions.
tags: [ci, github-actions, verification]
timestamp: 2026-07-11T17:20:40Z
status: accepted
---

# Status

Accepted by Lila Brooks on 2026-07-11.

# Context

Repo Pulse has a local verification contract: `make test`, Python compile checks, and `bash scripts/okf check-stale`. Those checks worked locally, but GitHub did not run them on pushes or pull requests. The README also needed a truthful CI badge, which requires a committed workflow.

The repo is Python-only and has no Node toolchain, no deployment target, and no build artifact. CI should mirror local verification without adding release or hosting behavior.

# Decision

Use GitHub Actions for CI in `.github/workflows/ci.yml`.

The workflow runs on pushes to `main`, pull requests, and manual dispatch. It uses Ubuntu, Python 3.12, `actions/checkout@v7`, and `actions/setup-python@v6` with pip caching. It runs:

- `make test`
- `.venv/bin/python -m compileall -q app tests`
- `bash scripts/okf check-stale`, with the PR base SHA or previous push SHA as the diff base when available

The workflow grants read-only repository contents permission. It does not deploy, publish, upload artifacts, or call the live GitHub API through the app.

Dependabot tracks GitHub Actions versions in `.github/dependabot.yml` alongside the Python dependency manifest.

# Alternatives considered

- Local-only verification: simpler, but pull requests and direct pushes would not show a visible pass/fail signal on GitHub.
- Add only `make test`: too narrow, because the repo's workflow also requires compile checks and OKF stale-map checks after changes.
- Add a Python version matrix: more coverage, but the goal fixes Python 3.12+ and the local environment currently verifies the app behavior. A matrix can be added later if compatibility across versions becomes an active maintenance target.
- Add deployment or Pages publishing: out of scope. The app is local-only by design.

# Consequences

Pull requests and pushes now get a visible CI result, and the README CI badge has a real workflow behind it. Dependency and workflow updates remain reviewable through Dependabot.

CI is another maintained surface: workflow actions, Python setup, and OKF diff-base behavior may need small updates over time. The workflow must stay in sync with the local verification commands documented in `AGENTS.md`, `docs/GOAL.md`, and the README.

# Rollback / revisit trigger

Revisit if GitHub Actions becomes noisy, too slow, unavailable for the repo's needs, or if verification moves to another required platform. Rollback is deleting `.github/workflows/ci.yml`, removing the CI badge, and removing the `github-actions` Dependabot entry.
