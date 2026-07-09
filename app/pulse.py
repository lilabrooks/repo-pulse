"""Compute the pulse verdict from a normalized repository summary."""

from datetime import datetime, timezone

ACTIVE_DAYS = 7
QUIET_DAYS = 90


def _days_since(iso_timestamp: str | None) -> int | None:
    if not iso_timestamp:
        return None
    pushed = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - pushed).days


def verdict(summary: dict) -> dict:
    """Return {"verdict": ..., "reasons": [...]} per docs/specs/api.md."""
    reasons: list[str] = []

    if summary["repo"]["archived"]:
        return {
            "verdict": "archived",
            "reasons": ["repository is archived and read-only"],
        }

    days = _days_since(summary["activity"]["last_push"])
    commits = summary["activity"]["commits_last_30d"]

    if days is None:
        reasons.append("no recorded pushes")
        result = "dormant"
    elif days <= ACTIVE_DAYS:
        reasons.append(f"last push {days} day(s) ago")
        result = "active"
    elif days <= QUIET_DAYS:
        reasons.append(f"last push {days} day(s) ago")
        result = "quiet"
    else:
        reasons.append(f"last push {days} day(s) ago")
        result = "dormant"

    reasons.append(f"{commits} commit(s) in the last 30 days")
    return {"verdict": result, "reasons": reasons}
