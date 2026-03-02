"""Tests for cache MCP tools.

Zero-mock policy: tests use the real in-memory Cache via the MCP tool functions.
Each test uses a unique cache name to avoid cross-test state. The module-level
manager singleton is reset via autouse fixture.
"""

from __future__ import annotations

import uuid

import pytest


@pytest.fixture(autouse=True)
def reset_cache_manager():
    """Reset the module-level CacheManager singleton between tests."""
    import codomyrmex.cache.mcp_tools as _mod
    _mod._manager = None
    yield
    _mod._manager = None


def _unique_cache() -> str:
    """Return a unique cache name to isolate tests."""
    return f"test_{uuid.uuid4().hex[:8]}"


def test_import_mcp_tools() -> None:
    """All four MCP tools are importable without errors."""
    from codomyrmex.cache.mcp_tools import (
        cache_delete,
        cache_get,
        cache_set,
        cache_stats,
    )

    assert callable(cache_get)
    assert callable(cache_set)
    assert callable(cache_delete)
    assert callable(cache_stats)


def test_cache_get_missing_returns_none() -> None:
    """cache_get returns None for a key that has never been set."""
    from codomyrmex.cache.mcp_tools import cache_get

    assert cache_get("nonexistent_key_xyzzy", cache_name=_unique_cache()) is None


def test_cache_set_returns_true() -> None:
    """cache_set returns True on success."""
    from codomyrmex.cache.mcp_tools import cache_set

    result = cache_set("k1", "v1", cache_name=_unique_cache())
    assert result is True


def test_cache_get_after_set() -> None:
    """cache_get returns the stored value after cache_set."""
    from codomyrmex.cache.mcp_tools import cache_get, cache_set

    cache_name = _unique_cache()
    cache_set("my_key", "my_value", cache_name=cache_name)
    assert cache_get("my_key", cache_name=cache_name) == "my_value"


def test_cache_delete_returns_true_when_exists() -> None:
    """cache_delete returns True when the key was present."""
    from codomyrmex.cache.mcp_tools import cache_delete, cache_set

    cache_name = _unique_cache()
    cache_set("to_del", 42, cache_name=cache_name)
    assert cache_delete("to_del", cache_name=cache_name) is True


def test_cache_delete_returns_false_when_missing() -> None:
    """cache_delete returns False for a key that was never set."""
    from codomyrmex.cache.mcp_tools import cache_delete

    assert cache_delete("never_set_xyzzy", cache_name=_unique_cache()) is False


def test_cache_stats_returns_dict() -> None:
    """cache_stats returns a dict with standard stat keys."""
    from codomyrmex.cache.mcp_tools import cache_stats

    stats = cache_stats(cache_name=_unique_cache())
    assert isinstance(stats, dict)
    assert "hits" in stats
    assert "misses" in stats


def test_cache_stats_hit_rate_after_operations() -> None:
    """hit_rate in stats reflects get operations after set."""
    from codomyrmex.cache.mcp_tools import cache_get, cache_set, cache_stats

    cache_name = _unique_cache()
    cache_set("k", "v", cache_name=cache_name)
    cache_get("k", cache_name=cache_name)      # hit
    cache_get("missing", cache_name=cache_name)  # miss
    stats = cache_stats(cache_name=cache_name)
    # Should have at least 1 hit and 1 miss recorded
    assert stats["hits"] >= 1
    assert stats["misses"] >= 1


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.cache.mcp_tools import (
        cache_delete,
        cache_get,
        cache_set,
        cache_stats,
    )

    for fn in (cache_get, cache_set, cache_delete, cache_stats):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
