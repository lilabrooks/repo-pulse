# Log

## 2026-07-09

- Milestone 1 (skeleton): FastAPI app with `/api/health` and the static index shell, pytest harness, and Makefile (`make test`, `make run`). Stack decision recorded as proposed ADR 0001 (FastAPI/uvicorn/httpx/pytest) per the decision policy — awaiting owner review. API contract started in `docs/specs/api.md` (health + index routes). Project ignores added for `.venv/`, `__pycache__/`, bytecode, and pytest cache.
- Known deprecation: starlette TestClient warns that `httpx` support is deprecated in favor of `httpx2`; tests pass, revisit with ADR 0001 if it breaks.
- Milestone 2 (GitHub summary API): `GET /api/repo/{owner}/{repo}` normalizes repo facts, open issues vs PRs (Link-header count), latest release, 30-day commit activity, and the pulse verdict; 404 and rate-limit errors mapped per spec. `docs/specs/api.md` carries the full contract and testability note; suite runs offline via httpx.MockTransport.
