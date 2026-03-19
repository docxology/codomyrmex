"""MCP tools for the ide module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="ide")
def ide_get_active_file() -> dict:
    """Return the currently active file in the IDE.

    Uses artifact mtime scanning and cwd heuristics to determine which
    file is most recently active in the Antigravity IDE.

    Returns:
        Dictionary with the active file path, or None if not determinable.
    """
    try:
        from codomyrmex.ide.antigravity.client import AntigravityClient

        client = AntigravityClient()
        active = client.get_active_file()
        return {
            "status": "success",
            "active_file": active,
            "found": active is not None,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="ide")
def ide_list_tools() -> dict:
    """List all available Antigravity IDE tools.

    Returns the full list of tool names that the Antigravity IDE exposes
    for programmatic invocation via the relay CLI.

    Returns:
        Dictionary with a list of tool names.
    """
    try:
        from codomyrmex.ide.antigravity.client import AntigravityClient

        tools = AntigravityClient.TOOLS
        return {
            "status": "success",
            "tools": list(tools),
            "count": len(tools),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
