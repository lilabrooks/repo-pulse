---
type: ADR
title: Resolve project homepages to GitHub repositories
description: Proposed scope change to accept non-GitHub URLs (e.g. a product homepage) and resolve them to owner/repo. Not implemented.
tags: [scope, frontend, github, security]
timestamp: 2026-07-09T00:00:00Z
owner: Lila Brooks
deciders: [Lila Brooks]
status: proposed
---

# Status

Proposed — **for review only, not implemented.** This ADR also requires a change
to `docs/GOAL.md` (Constraints and Non-goals), which is reserved for the owner.
Nothing ships until both this ADR is accepted and the goal is amended.

# Context

The dashboard input accepts `owner/repo`, `github.com/owner/repo`, and full
`https://github.com/...` URLs (see `docs/specs/frontend.md`). It deliberately
rejects non-GitHub hosts with a clear message, because `docs/GOAL.md` fixes
external data to "the GitHub REST API v3 only," and a product homepage carries no
REST-derivable `owner/repo`.

The trigger was a real paste: `lenshq.io/products/lens-k8s-ide`. That is the Lens
IDE homepage; its repository actually lives at `lensapp/lens`. A user who only
knows the product URL has no obvious path to the repo slug. Supporting this means
mapping an arbitrary homepage to its GitHub repository — a new capability that
crosses the current data-source constraint.

# Decision (proposed)

Relax the "GitHub REST API v3 only" constraint to allow one additional, bounded
lookup whose sole job is to turn a non-GitHub URL into a candidate `owner/repo`,
which then flows through the existing `fetch_summary` path unchanged. Because the
mapping is inherently heuristic, the resolver returns **candidates for the user to
confirm**, never an automatic redirect to a guessed repo.

Mechanism — three options, recommended first:

1. **GitHub Search API (`GET /search/repositories`).** Query by the product name
   (derived from the URL) and/or `homepage:` qualifier, show the top few matches
   with stars/description, let the user pick. Stays closest to the current
   constraint (Search is part of REST v3), needs no new dependency, and adds no
   outbound fetch to user-supplied hosts. Downsides: the Search API has its own
   stricter rate limit (10 req/min unauthenticated, 30 authenticated), and name
   matching is fuzzy — `lens` alone is ambiguous, so results must be shown, not
   auto-selected.
2. **Scrape the homepage for a GitHub link.** Fetch the pasted URL server-side and
   extract the first `github.com/owner/repo` link. Often exact when a project
   links its repo. Downsides: **fetching arbitrary user-supplied URLs is an SSRF
   surface** (a security-sensitive change per the guardrails — would require host
   allow-listing, blocking private/link-local ranges, timeouts, and size caps),
   plus it is fragile and many pages bury or omit the link.
3. **Third-party web search API.** Most general, worst fit: a new runtime
   dependency and API key to manage, per-query cost, non-deterministic results,
   and it breaks the offline-test criterion unless fully mocked.

Recommended: option 1, gated behind explicit user confirmation of a candidate.

# Alternatives considered

- **Keep the status quo (do nothing).** The clear "non-GitHub URL" error already
  tells the user what to enter. Zero new surface, zero accuracy risk. This remains
  the default if the resolver's accuracy or security cost is judged too high.
- **Client-side only resolution.** Not viable: browsers cannot fetch cross-origin
  homepages (CORS) or call the Search API without exposing rate-limit behavior the
  backend already centralizes. Any resolver belongs on the backend.

# Consequences

- New API surface (e.g. `GET /api/resolve?url=...`) returning ranked candidates,
  plus frontend UI to present and confirm them — a visible behavior change to
  `docs/specs/api.md` and `docs/specs/frontend.md`.
- Accuracy is best-effort; the user must confirm, so "wrong guess" degrades to "no
  match" rather than showing the wrong repo's vital signs.
- If option 2 is ever chosen, it is a security-sensitive change requiring input
  validation at the fetch boundary and its own `adr-suggest` pass.
- `docs/GOAL.md` Constraints ("GitHub REST API v3 only") and the "no private-repo
  / read-only" framing need amending to name the resolution step and its bound.

# Rollback / revisit trigger

Ship behind nothing else; if resolver matches prove noisy or the Search API rate
limit degrades the core flow, remove the resolve endpoint and revert to the
current clear-error behavior — the change is additive and isolated to a new
endpoint plus optional UI, so removal is contained. Revisit if GitHub tightens or
removes the Search API, or if demand appears for non-GitHub forges (GitLab,
Codeberg), which would widen the constraint further and warrant its own ADR.
