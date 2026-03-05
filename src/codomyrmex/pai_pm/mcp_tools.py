"""MCP tool definitions for the pai_pm module.

Exposes the PAI Project Manager server lifecycle and API as MCP tools.
All tools use stdlib HTTP (no extra deps) and return structured dicts.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_manager():
    """Lazy import of PaiPmServerManager."""
    from codomyrmex.pai_pm.server_manager import PaiPmServerManager

    return PaiPmServerManager()


def _get_client():
    """Lazy import of PaiPmClient."""
    from codomyrmex.pai_pm.client import PaiPmClient

    return PaiPmClient()


@mcp_tool(
    category="pai_pm",
    description="Start the PAI Project Manager server (Bun/TypeScript).",
)
def pai_pm_start() -> dict[str, Any]:
    """Start the PAI PM server as a background subprocess.

    Returns:
        dict with keys: status, pid, port, host
    """
    try:
        mgr = _get_manager()
        return mgr.start()
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="pai_pm",
    description="Stop the PAI Project Manager server.",
)
def pai_pm_stop() -> dict[str, Any]:
    """Stop the PAI PM server via SIGTERM.

    Returns:
        dict with keys: status, pid
    """
    try:
        mgr = _get_manager()
        return mgr.stop()
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="pai_pm",
    description="Check PAI PM server health (GET /api/health).",
)
def pai_pm_health() -> dict[str, Any]:
    """Check whether the PAI PM server is running and healthy.

    Returns:
        dict with keys: running (bool), and optionally status, port, uptime
    """
    try:
        mgr = _get_manager()
        if not mgr.is_running():
            return {"running": False}
        client = _get_client()
        data = client.health()
        data["running"] = True
        return data
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="pai_pm",
    description="Get PAI PM dashboard state (missions, projects, tasks).",
)
def pai_pm_get_state() -> dict[str, Any]:
    """Fetch full dashboard state from the PAI PM server.

    Returns:
        dict with keys: missions, projects, orphan_projects, stats
    """
    try:
        client = _get_client()
        return client.get_state()
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="pai_pm",
    description="Get agent awareness context from the PAI PM server.",
)
def pai_pm_get_awareness() -> dict[str, Any]:
    """Fetch agent awareness context (active work, priorities).

    Returns:
        dict with awareness data
    """
    try:
        client = _get_client()
        return client.get_awareness()
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="pai_pm",
    description="Dispatch an action via the PAI PM server (POST /api/dispatch/execute).",
)
def pai_pm_dispatch(
    action: str,
    backend: str = "",
    model: str = "",
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Dispatch an action to the PAI PM server for execution.

    Args:
        action: Action name to dispatch.
        backend: Optional backend identifier (e.g. 'claude', 'gemini').
        model: Optional model override.
        context: Optional context dict passed to the action.

    Returns:
        dict with dispatch result or job reference
    """
    try:
        client = _get_client()
        return client.dispatch_execute(action, backend=backend, model=model, context=context)
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
