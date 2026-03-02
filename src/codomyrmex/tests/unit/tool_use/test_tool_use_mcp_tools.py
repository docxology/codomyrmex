"""Tests for tool_use MCP tools.

Zero-mock policy: tests use the real tool_use module classes.
"""

from __future__ import annotations


def test_import_mcp_tools() -> None:
    """Both MCP tools are importable without errors."""
    from codomyrmex.tool_use.mcp_tools import (
        tool_use_list_tools,
        tool_use_validate_input,
    )

    assert callable(tool_use_list_tools)
    assert callable(tool_use_validate_input)


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.tool_use.mcp_tools import (
        tool_use_list_tools,
        tool_use_validate_input,
    )

    for fn in (tool_use_list_tools, tool_use_validate_input):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
        assert fn._mcp_tool_meta.get("category") == "tool_use"


def test_list_tools_returns_list() -> None:
    """tool_use_list_tools returns a list (possibly empty)."""
    from codomyrmex.tool_use.mcp_tools import tool_use_list_tools

    result = tool_use_list_tools()
    assert isinstance(result, list)


def test_validate_input_valid_data() -> None:
    """tool_use_validate_input returns dict with 'valid' key."""
    from codomyrmex.tool_use.mcp_tools import tool_use_validate_input

    result = tool_use_validate_input(
        schema={"type": "object"},
        data={"key": "value"},
    )
    assert isinstance(result, dict)
    assert "valid" in result
    assert isinstance(result["valid"], bool)


def test_validate_input_returns_errors_key() -> None:
    """Validation result includes an 'errors' key."""
    from codomyrmex.tool_use.mcp_tools import tool_use_validate_input

    result = tool_use_validate_input(
        schema={"type": "string"},
        data=42,
    )
    assert isinstance(result, dict)
    assert "errors" in result
