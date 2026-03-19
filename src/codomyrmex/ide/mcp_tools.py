"""MCP tools for the ide module."""

from __future__ import annotations

import os
from pathlib import Path

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _resolve_cursor_workspace(workspace_path: str | None) -> Path:
    """Resolve workspace root for CursorClient (explicit path, env, or cwd)."""
    if workspace_path:
        return Path(workspace_path).expanduser().resolve()
    env = os.getenv("CODOMYRMEX_CURSOR_WORKSPACE")
    if env:
        return Path(env).expanduser().resolve()
    return Path.cwd().resolve()


@mcp_tool(category="ide")
def ide_get_active_file() -> dict:
    """Return the currently active file in the Antigravity IDE.

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
            "backend": "antigravity",
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "backend": "antigravity"}


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
            "backend": "antigravity",
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "backend": "antigravity"}


@mcp_tool(category="ide")
def ide_cursor_workspace_info(workspace_path: str | None = None) -> dict:
    """Summarize a Cursor workspace using filesystem-backed CursorClient state.

    Workspace resolution order: ``workspace_path`` argument, then environment
    variable ``CODOMYRMEX_CURSOR_WORKSPACE``, then current working directory.

    Returns:
        Connection outcome, resolved workspace path, and capability metadata.
    """
    try:
        from codomyrmex.ide.cursor import CursorClient

        root = _resolve_cursor_workspace(workspace_path)
        client = CursorClient(str(root))
        connected = client.connect()
        caps = client.get_capabilities()
        cursor_dir = root / ".cursor"
        rules_path = root / ".cursorrules"
        return {
            "status": "success",
            "backend": "cursor",
            "workspace": str(root),
            "connected": connected,
            "ide_status": caps.get("status"),
            "cursor_dir_exists": cursor_dir.is_dir(),
            "cursorrules_exists": rules_path.is_file(),
            "capabilities": {
                "features": caps.get("features"),
                "models": caps.get("models"),
                "active_model": caps.get("active_model"),
                "supported_commands": caps.get("supported_commands"),
            },
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "backend": "cursor"}


@mcp_tool(category="ide")
def ide_cursor_get_active_file(workspace_path: str | None = None) -> dict:
    """Return the most recently modified source file under a Cursor workspace.

    Uses the same heuristic as ``CursorClient.get_active_file()`` (mtime scan).
    Workspace resolution matches ``ide_cursor_workspace_info``.
    """
    try:
        from codomyrmex.ide.cursor import CursorClient

        root = _resolve_cursor_workspace(workspace_path)
        client = CursorClient(str(root))
        if not client.connect():
            return {
                "status": "error",
                "message": "Could not connect to workspace",
                "workspace": str(root),
                "backend": "cursor",
            }
        active = client.get_active_file()
        return {
            "status": "success",
            "active_file": active,
            "found": active is not None,
            "workspace": str(root),
            "backend": "cursor",
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "backend": "cursor"}


@mcp_tool(category="ide")
def ide_cursor_rules_read(
    workspace_path: str | None = None, max_chars: int = 12000
) -> dict:
    """Read ``.cursorrules`` from a Cursor workspace with a bounded payload size.

    ``max_chars`` is clamped between 1 and 512_000. If content is longer, the
    response includes ``truncated: true`` and ``content`` is a prefix.

    Workspace resolution matches ``ide_cursor_workspace_info``.
    """
    try:
        from codomyrmex.ide.cursor import CursorClient

        cap = min(max(max_chars, 1), 512_000)
        root = _resolve_cursor_workspace(workspace_path)
        client = CursorClient(str(root))
        if not client.connect():
            return {
                "status": "error",
                "message": "Could not connect to workspace",
                "workspace": str(root),
                "backend": "cursor",
            }
        rules = client.get_rules()
        if rules.get("error"):
            return {
                "status": "error",
                "message": str(rules["error"]),
                "workspace": str(root),
                "backend": "cursor",
            }
        content = rules.get("content", "")
        if not isinstance(content, str):
            content = str(content)
        truncated = len(content) > cap
        out = content[:cap] if truncated else content
        return {
            "status": "success",
            "path": rules.get("path", str(root / ".cursorrules")),
            "exists": rules.get("exists", True),
            "truncated": truncated,
            "total_chars": len(content),
            "content": out,
            "workspace": str(root),
            "backend": "cursor",
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "backend": "cursor"}
