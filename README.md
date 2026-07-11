# Repo Pulse

Vital signs for any public GitHub repository. Enter `owner/repo` and get stars,
open issues vs. open pull requests, the latest release, 30-day commit activity,
and a computed pulse verdict — one page instead of six GitHub tabs.

Local-only by design: a FastAPI backend consuming the GitHub REST API v3, a
hand-written static dashboard, a 5-minute in-memory cache. No database, no
accounts, no Node toolchain.

## Requirements

- Python 3.12+ (invoked as `python3`)
- `make`
- Internet access to reach `api.github.com` (the test suite needs none)

## Quickstart

```console
git clone <url-of-this-repo> repo-pulse
cd repo-pulse
make run
```

The first run creates `.venv/` and installs the four dependencies (FastAPI,
uvicorn, httpx, pytest), then serves the app on port 8000:

- Dashboard: open <http://localhost:8000> and enter a repository. The form
  accepts `owner/repo`, `github.com/owner/repo`, or a full
  `https://github.com/owner/repo` URL (extra path, query, and a trailing `.git`
  are stripped). A non-GitHub URL is rejected with a hint, since repository data
  comes from the GitHub REST API only.
- Health check: `curl http://localhost:8000/api/health` returns
  `{"status":"ok"}`.
- Summary API: `curl http://localhost:8000/api/repo/psf/requests` returns the
  JSON the dashboard renders (contract in [docs/specs/api.md](docs/specs/api.md)).

## Tests

```console
make test
```

The suite is fully offline: every GitHub interaction is mocked through
`httpx.MockTransport`, so it passes with no network and no token.

## Higher rate limits (optional)

Anonymous GitHub API access allows 60 requests/hour per IP, and one uncached
dashboard query costs four. A token raises the limit to 5,000/hour:

```console
cp .env.example .env    # git-ignored; never commit a real token
# edit .env and set GITHUB_TOKEN=<your token>
make run                # loads .env when present
```

Exporting `GITHUB_TOKEN` in your shell works too. Either way, repeat queries
for the same repository are answered from the in-memory cache for 5 minutes
and cost no GitHub calls. If the token is invalid, the API answers 502 with
guidance — fix or unset it and restart.

## The pulse verdict

| Verdict | Meaning |
|---|---|
| `active` | pushed within the last 7 days |
| `quiet` | pushed within the last 90 days |
| `dormant` | no push in over 90 days, or never pushed (empty repository) |
| `archived` | repository is archived and read-only — overrides the others |

Unknown or private repositories return 404; an exhausted GitHub rate limit
returns 503 with guidance. The dashboard shows both as inline errors.

## Project layout

| Path | Contents |
|---|---|
| `app/` | FastAPI backend: routes, GitHub client, TTL cache, pulse verdict |
| `static/` | the dashboard — hand-written HTML/CSS/JS, no build step |
| `tests/` | offline pytest suite |
| `docs/GOAL.md` | goal, success criteria, milestone backlog |
| `docs/specs/` | API and frontend contracts |
| `docs/adr/` | architecture decision records |

## License

MIT. See [LICENSE](LICENSE).

## Origins

This repository was scaffolded from the
[claude-okf-repo-kit](https://github.com/lilabrooks/claude-okf-repo-kit) — the
OKF workflow starter that provides `CLAUDE.md`, the `docs/` knowledge bundle
(goal, specs, ADRs, log), and the `.claude/` hooks. Everything under `app/`,
`static/`, and `tests/` was built on top of that scaffold.

One notable enhancement beyond the original milestones: the dashboard input
parser (`static/app.js`) was widened to accept full GitHub URLs and
`github.com/owner/repo`, not just a bare `owner/repo` slug — it strips the
scheme, a leading `www.`, the `github.com` host, a trailing `.git`, and any
extra path/query/fragment before calling the API, and rejects non-GitHub hosts
with a clear message. Extending that to resolve arbitrary project homepages
(e.g. a product landing page) to their repository is captured as a proposed,
unimplemented scope change in
[docs/adr/0003](docs/adr/0003-homepage-to-repo-resolution.md).
