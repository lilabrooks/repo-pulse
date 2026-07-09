import pytest

from app import cache


@pytest.fixture(autouse=True)
def fresh_cache():
    """Isolate the process-local summary cache between tests (ADR 0002)."""
    cache.clear()
    yield
    cache.clear()
