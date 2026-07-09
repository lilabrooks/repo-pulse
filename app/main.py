"""Repo Pulse backend: JSON API plus the static dashboard."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import github, pulse

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Repo Pulse")


@app.get("/api/health")
def health() -> dict:
    """Liveness check per docs/specs/api.md."""
    return {"status": "ok"}


@app.get("/api/repo/{owner}/{repo}")
def repo_summary(owner: str, repo: str) -> dict:
    """Normalized repository summary per docs/specs/api.md."""
    try:
        summary = github.fetch_summary(owner, repo)
    except github.RepoNotFound:
        raise HTTPException(status_code=404, detail="repository not found")
    except github.RateLimited:
        raise HTTPException(
            status_code=503,
            detail=(
                "GitHub rate limit exceeded; try again later or set "
                "GITHUB_TOKEN for a higher limit"
            ),
        )
    summary["pulse"] = pulse.verdict(summary)
    return summary


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
