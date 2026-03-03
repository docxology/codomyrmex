"""Unit tests for the meme MCP tools."""

from codomyrmex.meme.mcp_tools import register_tools


def test_register_tools_returns_empty_list():
    """Test that register_tools returns an empty list.

    As per MCP_TOOL_SPECIFICATION.md, the meme module currently exposes no
    MCP tools.
    """
    tools = register_tools()
    assert tools == []
    assert isinstance(tools, list)
