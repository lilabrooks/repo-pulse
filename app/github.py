"""GitHub REST v3 consumption: fetch and normalize a repository summary.

All network access goes through the httpx.Client built by make_client(), so
tests inject an httpx.MockTransport and the suite runs fully offline.
"""

import re
from datetime import datetime, timedelta, timezone

import httpx

API_ROOT = "https://api.github.com"
USER_AGENT = "repo-pulse (local dashboard)"
ACTIVITY_WINDOW_DAYS = 30


class RepoNotFound(Exception):
    """The repository does not exist or is not public."""


class RateLimited(Exception):
    """GitHub rejected the request because the rate limit is exhausted."""


def make_client(transport: httpx.BaseTransport | None = None) -> httpx.Client:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
    }
    return httpx.Client(
        base_url=API_ROOT, headers=headers, timeout=10, transport=transport
    )


def _get(client: httpx.Client, path: str, **params) -> httpx.Response:
    response = client.get(path, params=params or None)
    if response.status_code == 404:
        raise RepoNotFound(path)
    if response.status_code in (403, 429) and response.headers.get(
        "x-ratelimit-remaining"
    ) == "0":
        raise RateLimited(path)
    response.raise_for_status()
    return response


def _open_pr_count(client: httpx.Client, owner: str, repo: str) -> int:
    """Count open PRs via the per_page=1 Link-header trick (no search API)."""
    response = _get(
        client, f"/repos/{owner}/{repo}/pulls", state="open", per_page=1
    )
    link = response.headers.get("link", "")
    match = re.search(r'[?&]page=(\d+)>; rel="last"', link)
    if match:
        return int(match.group(1))
    return len(response.json())


def _latest_release(client: httpx.Client, owner: str, repo: str) -> dict | None:
    try:
        data = _get(client, f"/repos/{owner}/{repo}/releases/latest").json()
    except RepoNotFound:
        return None  # repo exists but has no releases
    return {
        "tag": data.get("tag_name"),
        "name": data.get("name"),
        "published_at": data.get("published_at"),
    }


def _commits_last_window(client: httpx.Client, owner: str, repo: str) -> int:
    since = datetime.now(timezone.utc) - timedelta(days=ACTIVITY_WINDOW_DAYS)
    response = client.get(
        f"/repos/{owner}/{repo}/commits",
        params={"since": since.isoformat(), "per_page": 100},
    )
    if response.status_code == 409:  # empty repository
        return 0
    if response.status_code == 404:
        raise RepoNotFound(f"{owner}/{repo}")
    response.raise_for_status()
    return len(response.json())


def fetch_summary(owner: str, repo: str, client: httpx.Client | None = None) -> dict:
    """Return the normalized summary defined in docs/specs/api.md."""
    own_client = client is None
    client = client or make_client()
    try:
        info = _get(client, f"/repos/{owner}/{repo}").json()
        open_prs = _open_pr_count(client, owner, repo)
        release = _latest_release(client, owner, repo)
        commits = _commits_last_window(client, owner, repo)
    finally:
        if own_client:
            client.close()

    open_issues = max(0, info.get("open_issues_count", 0) - open_prs)
    license_info = info.get("license") or {}
    return {
        "repo": {
            "full_name": info.get("full_name"),
            "description": info.get("description"),
            "html_url": info.get("html_url"),
            "stars": info.get("stargazers_count", 0),
            "forks": info.get("forks_count", 0),
            "watchers": info.get("subscribers_count", 0),
            "archived": bool(info.get("archived", False)),
            "license": license_info.get("spdx_id"),
        },
        "issues": {"open_issues": open_issues, "open_prs": open_prs},
        "release": release,
        "activity": {
            "commits_last_30d": commits,
            "last_push": info.get("pushed_at"),
        },
    }
