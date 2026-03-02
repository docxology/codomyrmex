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
def ide_list_integrations() -> dict:
    """List available IDE integrations.

    Returns the names of the supported IDE integrations that can be connected to.

    Returns:
        Dictionary with a list of available IDE integrations.
    """
    return {
        "status": "success",
        "integrations": ["antigravity", "cursor", "vscode"],
    }


def _get_client(integration: str):
    """Helper to get the corresponding IDE client."""
    if integration == "antigravity":
        from codomyrmex.ide.antigravity.client import AntigravityClient

        return AntigravityClient()
    elif integration == "cursor":
        from codomyrmex.ide.cursor import CursorClient

        return CursorClient()
    elif integration == "vscode":
        from codomyrmex.ide.vscode import VSCodeClient

        return VSCodeClient()
    else:
        raise ValueError(f"Unknown IDE integration: {integration}")


@mcp_tool(category="ide")
def ide_get_status(integration: str) -> dict:
    """Get the connection status of a specified IDE integration.

    Args:
        integration: The name of the IDE integration ("antigravity", "cursor", "vscode").

    Returns:
        Dictionary with the connection status or error.
    """
    try:
        client = _get_client(integration)
        client.connect()
        return {
            "status": "success",
            "integration": integration,
            "connection_status": client.status.value,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="ide")
def ide_execute_command(
    integration: str, command: str, args: dict | None = None
) -> dict:
    """Execute an IDE command on a specified integration.

    Args:
        integration: The name of the IDE integration ("antigravity", "cursor", "vscode").
        command: The command to execute.
        args: Optional arguments for the command.

    Returns:
        Dictionary with the execution result or error.
    """
    try:
        client = _get_client(integration)
        client.connect()
        result = client.execute_command_safe(command, args=args)
        return {
            "status": "success",
            "integration": integration,
            "result": result.to_dict(),
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
