"""Tests for testing MCP tools.

Zero-mock policy: tests use the real generator strategies.
"""

from __future__ import annotations

import pytest


def test_import_mcp_tools() -> None:
    """Both MCP tools are importable without errors."""
    from codomyrmex.testing.mcp_tools import (
        testing_generate_data,
        testing_list_strategies,
    )

    assert callable(testing_generate_data)
    assert callable(testing_list_strategies)


def test_list_strategies_returns_list() -> None:
    """testing_list_strategies returns a non-empty list of strings."""
    from codomyrmex.testing.mcp_tools import testing_list_strategies

    strategies = testing_list_strategies()
    assert isinstance(strategies, list)
    assert len(strategies) >= 4
    assert "int" in strategies
    assert "string" in strategies


def test_generate_int_data() -> None:
    """testing_generate_data returns a list of ints for strategy_type='int'."""
    from codomyrmex.testing.mcp_tools import testing_generate_data

    results = testing_generate_data("int", count=5)
    assert isinstance(results, list)
    assert len(results) == 5
    assert all(isinstance(v, int) for v in results)


def test_generate_string_data() -> None:
    """testing_generate_data returns a list of strings for strategy_type='string'."""
    from codomyrmex.testing.mcp_tools import testing_generate_data

    results = testing_generate_data("string", count=4, config={"min_length": 3, "max_length": 10})
    assert isinstance(results, list)
    assert len(results) == 4
    assert all(isinstance(v, str) for v in results)


def test_generate_list_data() -> None:
    """testing_generate_data returns a list of lists for strategy_type='list'."""
    from codomyrmex.testing.mcp_tools import testing_generate_data

    results = testing_generate_data("list", count=3)
    assert isinstance(results, list)
    assert len(results) == 3
    assert all(isinstance(v, list) for v in results)


def test_generate_unknown_strategy_raises() -> None:
    """testing_generate_data raises ValueError for an unknown strategy_type."""
    from codomyrmex.testing.mcp_tools import testing_generate_data

    with pytest.raises(ValueError, match="Unknown strategy_type"):
        testing_generate_data("nonexistent_xyzzy")


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.testing.mcp_tools import (
        testing_generate_data,
        testing_list_strategies,
    )

    for fn in (testing_generate_data, testing_list_strategies):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
