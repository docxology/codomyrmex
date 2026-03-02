"""Tests for vector_store MCP tools.

Zero-mock policy: tests use the real InMemoryVectorStore singleton via the
MCP tool functions.  Each test creates a fresh module-level store state by
resetting the singleton between tests.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def reset_vector_store():
    """Reset the module-level store before each test for isolation."""
    import codomyrmex.vector_store.mcp_tools as _mod
    _mod._store = None
    yield
    _mod._store = None


def test_import_mcp_tools() -> None:
    """All four MCP tools are importable without errors."""
    from codomyrmex.vector_store.mcp_tools import (
        vector_add,
        vector_count,
        vector_delete,
        vector_search,
    )
    assert callable(vector_add)
    assert callable(vector_search)
    assert callable(vector_delete)
    assert callable(vector_count)


def test_vector_count_empty_store() -> None:
    """An empty store reports count 0."""
    from codomyrmex.vector_store.mcp_tools import vector_count

    assert vector_count() == 0


def test_vector_add_returns_true() -> None:
    """vector_add returns True on success."""
    from codomyrmex.vector_store.mcp_tools import vector_add

    result = vector_add("v1", [0.1, 0.2, 0.3])
    assert result is True


def test_vector_add_increments_count() -> None:
    """Adding vectors increases the count."""
    from codomyrmex.vector_store.mcp_tools import vector_add, vector_count

    vector_add("a", [1.0, 0.0])
    vector_add("b", [0.0, 1.0])
    assert vector_count() == 2


def test_vector_search_returns_list() -> None:
    """vector_search returns a list of result dicts."""
    from codomyrmex.vector_store.mcp_tools import vector_add, vector_search

    vector_add("x", [1.0, 0.0, 0.0])
    vector_add("y", [0.0, 1.0, 0.0])
    results = vector_search([1.0, 0.0, 0.0], k=2)
    assert isinstance(results, list)
    assert len(results) <= 2
    for r in results:
        assert "id" in r
        assert "score" in r
        assert "metadata" in r


def test_vector_search_best_match_first() -> None:
    """The most similar vector is returned first."""
    from codomyrmex.vector_store.mcp_tools import vector_add, vector_search

    vector_add("match", [1.0, 0.0])
    vector_add("other", [0.0, 1.0])
    results = vector_search([1.0, 0.0], k=2)
    assert len(results) == 2
    assert results[0]["id"] == "match"


def test_vector_delete_returns_true() -> None:
    """vector_delete returns True when the vector exists."""
    from codomyrmex.vector_store.mcp_tools import vector_add, vector_delete

    vector_add("to_delete", [0.5, 0.5])
    assert vector_delete("to_delete") is True


def test_vector_delete_returns_false_not_found() -> None:
    """vector_delete returns False for an unknown ID."""
    from codomyrmex.vector_store.mcp_tools import vector_delete

    assert vector_delete("nonexistent_id_xyzzy") is False


def test_vector_delete_decrements_count() -> None:
    """Deleting a vector decreases the count."""
    from codomyrmex.vector_store.mcp_tools import (
        vector_add,
        vector_count,
        vector_delete,
    )

    vector_add("keep", [1.0, 0.0])
    vector_add("remove", [0.0, 1.0])
    vector_delete("remove")
    assert vector_count() == 1


def test_vector_add_with_metadata() -> None:
    """vector_add stores metadata and it is returned in search results."""
    from codomyrmex.vector_store.mcp_tools import vector_add, vector_search

    vector_add("meta_vec", [1.0, 0.0], metadata={"source": "test"})
    results = vector_search([1.0, 0.0], k=1)
    assert len(results) == 1
    assert results[0]["metadata"].get("source") == "test"


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.vector_store.mcp_tools import (
        vector_add,
        vector_count,
        vector_delete,
        vector_search,
    )
    for fn in (vector_add, vector_search, vector_delete, vector_count):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
