"""Offline tests for /api/repo/{owner}/{repo}: GitHub is fully mocked."""

from datetime import datetime, timedelta, timezone

import httpx
from fastapi.testclient import TestClient

from app import github, pulse
from app.main import app

client = TestClient(app)

RECENT_PUSH = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
QUIET_PUSH = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
OLD_PUSH = (datetime.now(timezone.utc) - timedelta(days=400)).isoformat()

REPO_INFO = {
    "full_name": "octo/hello",
    "description": "A test repository",
    "html_url": "https://github.com/octo/hello",
    "stargazers_count": 420,
    "forks_count": 55,
    "subscribers_count": 17,
    "open_issues_count": 12,
    "archived": False,
    "license": {"spdx_id": "MIT"},
    "pushed_at": RECENT_PUSH,
}

RELEASE = {"tag_name": "v1.2.3", "name": "One point two three", "published_at": "2026-06-30T12:00:00Z"}


def fake_github(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/repos/octo/hello":
        return httpx.Response(200, json=REPO_INFO)
    if path == "/repos/octo/hello/pulls":
        link = '<https://api.github.com/repos/octo/hello/pulls?state=open&per_page=1&page=4>; rel="last"'
        return httpx.Response(200, json=[{"number": 1}], headers={"link": link})
    if path == "/repos/octo/hello/releases/latest":
        return httpx.Response(200, json=RELEASE)
    if path == "/repos/octo/hello/commits":
        assert "since" in dict(request.url.params)
        return httpx.Response(200, json=[{"sha": "a"}, {"sha": "b"}, {"sha": "c"}])
    if path == "/repos/octo/norelease/releases/latest":
        return httpx.Response(404, json={"message": "Not Found"})
    if path.startswith("/repos/octo/norelease"):
        if path.endswith("/pulls"):
            return httpx.Response(200, json=[])
        if path.endswith("/commits"):
            return httpx.Response(200, json=[])
        return httpx.Response(200, json={**REPO_INFO, "full_name": "octo/norelease"})
    if path.startswith("/repos/octo/empty"):
        if path.endswith("/pulls"):
            return httpx.Response(200, json=[])
        if path.endswith("/releases/latest"):
            return httpx.Response(404, json={"message": "Not Found"})
        if path.endswith("/commits"):
            return httpx.Response(409, json={"message": "Git Repository is empty."})
        return httpx.Response(
            200,
            json={**REPO_INFO, "full_name": "octo/empty", "open_issues_count": 0, "pushed_at": None},
        )
    if path.startswith("/repos/octo/attic"):
        if path.endswith("/pulls"):
            return httpx.Response(200, json=[])
        if path.endswith("/releases/latest"):
            return httpx.Response(200, json=RELEASE)
        if path.endswith("/commits"):
            return httpx.Response(200, json=[{"sha": "a"}])
        return httpx.Response(200, json={**REPO_INFO, "full_name": "octo/attic", "archived": True})
    if path.startswith("/repos/octo/slowdown"):
        if path.endswith("/commits"):
            return httpx.Response(
                403,
                json={"message": "API rate limit exceeded"},
                headers={"x-ratelimit-remaining": "0"},
            )
        if path.endswith("/pulls"):
            return httpx.Response(200, json=[])
        if path.endswith("/releases/latest"):
            return httpx.Response(404, json={"message": "Not Found"})
        return httpx.Response(200, json={**REPO_INFO, "full_name": "octo/slowdown"})
    if path.startswith("/repos/octo/badtoken"):
        return httpx.Response(401, json={"message": "Bad credentials"})
    if path.startswith("/repos/octo/missing"):
        return httpx.Response(404, json={"message": "Not Found"})
    if path.startswith("/repos/octo/limited"):
        return httpx.Response(
            403,
            json={"message": "API rate limit exceeded"},
            headers={"x-ratelimit-remaining": "0"},
        )
    raise AssertionError(f"unexpected GitHub call: {path}")


def use_fake_github(monkeypatch):
    transport = httpx.MockTransport(fake_github)
    monkeypatch.setattr(
        github, "make_client", lambda t=transport: httpx.Client(
            base_url=github.API_ROOT, transport=t
        )
    )


def test_repo_summary_happy_path(monkeypatch):
    use_fake_github(monkeypatch)
    response = client.get("/api/repo/octo/hello")
    assert response.status_code == 200
    data = response.json()
    assert data["repo"]["full_name"] == "octo/hello"
    assert data["repo"]["stars"] == 420
    assert data["repo"]["license"] == "MIT"
    assert data["issues"] == {"open_issues": 8, "open_prs": 4}
    assert data["release"]["tag"] == "v1.2.3"
    assert data["activity"]["commits_last_30d"] == 3
    assert data["pulse"]["verdict"] == "active"


def test_repo_without_release_returns_null_release(monkeypatch):
    use_fake_github(monkeypatch)
    response = client.get("/api/repo/octo/norelease")
    assert response.status_code == 200
    assert response.json()["release"] is None


def test_unknown_repo_maps_to_404(monkeypatch):
    use_fake_github(monkeypatch)
    response = client.get("/api/repo/octo/missing")
    assert response.status_code == 404
    assert response.json()["detail"] == "repository not found"


def test_rate_limit_maps_to_503_with_guidance(monkeypatch):
    use_fake_github(monkeypatch)
    response = client.get("/api/repo/octo/limited")
    assert response.status_code == 503
    assert "GITHUB_TOKEN" in response.json()["detail"]


def test_empty_repo_is_dormant_with_no_pushes(monkeypatch):
    use_fake_github(monkeypatch)
    response = client.get("/api/repo/octo/empty")
    assert response.status_code == 200
    data = response.json()
    assert data["activity"] == {"commits_last_30d": 0, "last_push": None}
    assert data["release"] is None
    assert data["pulse"]["verdict"] == "dormant"
    assert "no recorded pushes" in data["pulse"]["reasons"]


def test_archived_repo_verdict_overrides_recent_activity(monkeypatch):
    use_fake_github(monkeypatch)
    response = client.get("/api/repo/octo/attic")
    assert response.status_code == 200
    data = response.json()
    assert data["repo"]["archived"] is True
    assert data["pulse"]["verdict"] == "archived"
    assert data["pulse"]["reasons"] == ["repository is archived and read-only"]


def test_rate_limit_during_commit_fetch_maps_to_503(monkeypatch):
    use_fake_github(monkeypatch)
    response = client.get("/api/repo/octo/slowdown")
    assert response.status_code == 503
    assert "GITHUB_TOKEN" in response.json()["detail"]


def test_bad_token_maps_to_502_with_guidance(monkeypatch):
    use_fake_github(monkeypatch)
    response = client.get("/api/repo/octo/badtoken")
    assert response.status_code == 502
    assert "GITHUB_TOKEN" in response.json()["detail"]


def test_pulse_quiet_when_push_within_90_days():
    summary = {
        "repo": {"archived": False},
        "activity": {"last_push": QUIET_PUSH, "commits_last_30d": 0},
    }
    assert pulse.verdict(summary)["verdict"] == "quiet"


def test_pulse_archived_overrides_activity():
    summary = {
        "repo": {"archived": True},
        "activity": {"last_push": RECENT_PUSH, "commits_last_30d": 9},
    }
    assert pulse.verdict(summary)["verdict"] == "archived"


def test_pulse_dormant_when_push_is_old():
    summary = {
        "repo": {"archived": False},
        "activity": {"last_push": OLD_PUSH, "commits_last_30d": 0},
    }
    result = pulse.verdict(summary)
    assert result["verdict"] == "dormant"
    assert any("last push" in reason for reason in result["reasons"])
