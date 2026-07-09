---
type: ADR
title: In-memory TTL cache for repo summaries
description: Cache normalized summaries in process memory for 5 minutes; optional GITHUB_TOKEN raises the upstream limit.
tags: [cache, rate-limit, github]
timestamp: 2026-07-09T00:00:00Z
owner: Lila Brooks
deciders: [Lila Brooks]
status: proposed
---

# Status

Proposed (authored by Claude Code per the decision policy; awaiting owner review)

# Context

Unauthenticated GitHub REST calls are limited to 60 requests/hour per IP, and one dashboard query costs 4 upstream calls. Re-querying the same repository — the common case while someone inspects a project — burns the budget fast. The goal requires rate-limit friendliness with no database and no persistence beyond memory.

# Decision

- Cache normalized summaries in a process-local dict keyed by `owner/repo`, with a 300-second TTL and a small time-injection seam so tests control expiry. No size cap: a local single-user dashboard cannot realistically grow it beyond a handful of entries.
- Support an optional `GITHUB_TOKEN` environment variable (5,000 requests/hour when set). The token is attached as a Bearer header at client construction, documented in a committed `.env.example`, and never tracked: `.env` and `.env.*` are git-ignored (with `!.env.example` kept trackable), per the security guardrail.

Alternatives considered:

- No cache, token only. Rejected: tokenless users hit the 60/hour wall after 15 dashboard queries.
- Disk cache (sqlite or JSON file). Rejected: persistence is a stated non-goal, and stale-on-restart semantics are fine for a local tool.
- HTTP-level caching with ETag/If-None-Match. Rejected for now: conditional requests still spend a request on 304s under the primary (core) limit budget accounting only when validation fails; a TTL answers the common case with zero calls. Revisit trigger below.

# Consequences

Summaries can be up to 5 minutes stale, which is acceptable for repository vital signs. Cache state vanishes on restart by design. Rollback/revisit trigger: if users need fresher data or memory ever matters, switch to ETag conditional requests behind the same `fetch_summary` seam — the cache is a wrapper, so the swap stays contained.
