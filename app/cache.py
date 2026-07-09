"""Process-local TTL cache for repo summaries (ADR 0002)."""

import time

TTL_SECONDS = 300

_store: dict[str, tuple[float, dict]] = {}


def get(key: str, now: float | None = None) -> dict | None:
    now = time.monotonic() if now is None else now
    entry = _store.get(key)
    if entry is None:
        return None
    stored_at, value = entry
    if now - stored_at > TTL_SECONDS:
        del _store[key]
        return None
    return value


def put(key: str, value: dict, now: float | None = None) -> None:
    now = time.monotonic() if now is None else now
    _store[key] = (now, value)


def clear() -> None:
    _store.clear()
