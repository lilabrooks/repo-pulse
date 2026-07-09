"""Cache and token behavior per ADR 0002; GitHub stays fully mocked."""

import httpx
from fastapi.testclient import TestClient

from app import cache, github
from app.main import app
from tests.test_repo_api import fake_github

client = TestClient(app)


def test_cache_expires_after_ttl():
    cache.put("k", {"v": 1}, now=1000.0)
    assert cache.get("k", now=1000.0 + cache.TTL_SECONDS) == {"v": 1}
    assert cache.get("k", now=1001.0 + cache.TTL_SECONDS) is None


def test_second_query_is_served_from_cache(monkeypatch):
    calls = []

    def counting_github(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return fake_github(request)

    transport = httpx.MockTransport(counting_github)
    monkeypatch.setattr(
        github, "make_client", lambda t=transport: httpx.Client(
            base_url=github.API_ROOT, transport=t
        )
    )

    first = client.get("/api/repo/octo/hello")
    calls_after_first = len(calls)
    second = client.get("/api/repo/octo/hello")

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert calls_after_first == 4  # repo, pulls, release, commits
    assert len(calls) == calls_after_first  # cache hit: zero new upstream calls


def test_errors_are_not_cached(monkeypatch):
    transport = httpx.MockTransport(fake_github)
    monkeypatch.setattr(
        github, "make_client", lambda t=transport: httpx.Client(
            base_url=github.API_ROOT, transport=t
        )
    )
    assert client.get("/api/repo/octo/missing").status_code == 404
    assert client.get("/api/repo/octo/missing").status_code == 404


def test_token_attached_only_when_env_is_set(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    assert "authorization" not in github.make_client().headers

    monkeypatch.setenv("GITHUB_TOKEN", "t-123")
    assert github.make_client().headers["authorization"] == "Bearer t-123"
