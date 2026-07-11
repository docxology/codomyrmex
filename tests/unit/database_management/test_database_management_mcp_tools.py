"""Tests for database_management MCP tools.

Zero-mock policy: tests use the real database_management functions.
"""

from __future__ import annotations


def test_import_mcp_tools() -> None:
    """All three MCP tools are importable without errors."""
    from codomyrmex.database_management.mcp_tools import (
        db_generate_schema,
        db_list_adapters,
        db_monitor,
    )

    assert callable(db_list_adapters)
    assert callable(db_monitor)
    assert callable(db_generate_schema)


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.database_management.mcp_tools import (
        db_generate_schema,
        db_list_adapters,
        db_monitor,
    )

    for fn in (db_list_adapters, db_monitor, db_generate_schema):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
        assert fn._mcp_tool_meta.get("category") == "database_management"


def test_list_adapters_returns_list() -> None:
    """db_list_adapters returns a non-empty list of strings."""
    from codomyrmex.database_management.mcp_tools import db_list_adapters

    result = db_list_adapters()
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(a, str) for a in result)


def test_list_adapters_includes_sqlite() -> None:
    """db_list_adapters always includes 'sqlite'."""
    from codomyrmex.database_management.mcp_tools import db_list_adapters

    assert "sqlite" in db_list_adapters()


def test_monitor_returns_dict() -> None:
    """db_monitor returns a dictionary of metrics."""
    from codomyrmex.database_management.mcp_tools import db_monitor

    result = db_monitor()
    assert isinstance(result, dict)


def test_generate_schema_returns_dict() -> None:
    """db_generate_schema produces a result dict."""
    from codomyrmex.database_management.mcp_tools import db_generate_schema

    result = db_generate_schema(
        models=[{"name": "TestModel", "fields": {"id": "int", "name": "str"}}],
    )
    assert isinstance(result, dict)
