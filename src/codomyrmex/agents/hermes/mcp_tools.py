"""MCP tool definitions for the Hermes coding agent module.

Exposes Hermes CLI single-turn chat execution and skill management as MCP tools.
All tools lazy-import HermesClient to avoid circular dependencies at collection time.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_client(command: str = "hermes", timeout: int = 120) -> Any:
    """Lazy import of HermesClient to avoid circular deps."""
    from codomyrmex.agents.hermes.hermes_client import HermesClient

    return HermesClient(config={"hermes_command": command, "hermes_timeout": timeout})


@mcp_tool(
    category="hermes",
    description=(
        "Check Hermes configuration and availability status. "
        "Returns diagnostics for the installed Hermes CLI."
    ),
)
def hermes_status() -> dict[str, Any]:
    """Check Hermes configuration.

    Returns:
        dict with keys: status, available, output, error (on failure)
    """
    try:
        client = _get_client()
        info = client.get_hermes_status()
        return {"status": "success", "available": info["success"], **info}
    except Exception as exc:
        return {"status": "error", "available": False, "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Execute a single-turn chat with the Hermes agent CLI. "
        "Hermes can perform tasks autonomously based on the prompt."
    ),
)
def hermes_execute(
    prompt: str,
    timeout: int = 120,
) -> dict[str, Any]:
    """Submit a prompt to Hermes using hermes chat -q.

    Args:
        prompt: Natural-language task description.
        timeout: Subprocess timeout in seconds (default 120).

    Returns:
        dict with keys: status, content, error, metadata
    """
    try:
        from codomyrmex.agents.core import AgentRequest
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        client = HermesClient(config={"hermes_timeout": timeout})
        request = AgentRequest(prompt=prompt)
        response = client.execute(request)
        return {
            "status": "success" if response.is_success() else "error",
            "content": response.content,
            "error": response.error,
            "metadata": response.metadata,
        }
    except Exception as exc:
        return {"status": "error", "content": "", "error": str(exc), "metadata": {}}


@mcp_tool(
    category="hermes",
    description=(
        "List all skills currently installed and available to the Hermes agent."
    ),
)
def hermes_skills_list() -> dict[str, Any]:
    """List available Hermes skills.

    Returns:
        dict with keys: status, output, or error info
    """
    try:
        client = _get_client(timeout=10)
        result = client.list_skills()
        if result.get("success"):
            return {"status": "success", "output": result.get("output", "")}
        return {
            "status": "error",
            "message": result.get("output", result.get("error", "Unknown erro")),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
