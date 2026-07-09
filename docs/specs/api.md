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

## GET /

Serves the dashboard `static/index.html`. Static assets are mounted under `/static/`.
