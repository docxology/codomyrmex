"""Strictly zero-mock unit tests for concurrency MCP tools."""

import pytest

from codomyrmex.concurrency import LocalLock, LockManager
from codomyrmex.concurrency.mcp_tools import (
    concurrency_list_locks,
    concurrency_pool_status,
)


@pytest.mark.unit
def test_concurrency_pool_status():
    """Test the concurrency_pool_status MCP tool."""
    result = concurrency_pool_status()

    assert isinstance(result, dict)
    assert result.get("status") == "success"

    pool_stats = result.get("pool_stats")
    assert isinstance(pool_stats, dict)

    expected_keys = {
        "submitted",
        "completed",
        "failed",
        "total_elapsed_ms",
    }
    for key in expected_keys:
        assert key in pool_stats
        assert isinstance(pool_stats[key], (int, float))


@pytest.mark.unit
def test_concurrency_list_locks():
    """Test the concurrency_list_locks MCP tool."""
    manager = LockManager()
    lock_name = "test_mcp_lock"
    lock = LocalLock(lock_name)
    manager.register_lock(lock_name, lock)

    result = concurrency_list_locks()

    assert isinstance(result, dict)
    assert result.get("status") == "success"
    assert "locks" in result
    assert isinstance(result.get("locks"), list)
    assert "count" in result
    assert isinstance(result.get("count"), int)

    assert len(result["locks"]) == result["count"]
