"""MCP tool definitions for the Hermes agent module.

Exposes Hermes chat execution, skills management, and status as MCP tools.
Automatically uses Ollama hermes3 when the Hermes CLI is unavailable.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_client(
    backend: str = "auto",
    model: str = "hermes3",
    timeout: int = 120,
) -> Any:
    """Lazy-instantiate HermesClient with the given configuration.

    Args:
        backend: ``"auto"`` | ``"cli"`` | ``"ollama"``
        model: Ollama model name (default ``hermes3``)
        timeout: Subprocess timeout in seconds
    """
    from codomyrmex.agents.hermes.hermes_client import HermesClient

    return HermesClient(config={
        "hermes_backend": backend,
        "hermes_model": model,
        "hermes_timeout": timeout,
    })


@mcp_tool(
    category="hermes",
    description=(
        "Check Hermes agent availability and configuration. "
        "Reports which backend (CLI / Ollama) is active."
    ),
)
def hermes_status() -> dict[str, Any]:
    """Check Hermes configuration.

    Returns:
        dict with active_backend, cli_available, ollama_available, ollama_model
    """
    try:
        client = _get_client()
        info = client.get_hermes_status()
        return {"status": "success", "available": info.get("success", False), **info}
    except Exception as exc:
        return {"status": "error", "available": False, "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Execute a single-turn chat with the Hermes agent. "
        "Uses the Hermes CLI if available, otherwise Ollama hermes3."
    ),
)
def hermes_execute(
    prompt: str,
    backend: str = "auto",
    model: str = "hermes3",
    timeout: int = 120,
) -> dict[str, Any]:
    """Submit a prompt to the Hermes agent.

    Args:
        prompt: Natural-language task description.
        backend: ``"auto"`` (default), ``"cli"``, or ``"ollama"``.
        model: Ollama model name (default ``hermes3``).
        timeout: Subprocess timeout in seconds (default 120).

    Returns:
        dict with keys: status, content, error, metadata
    """
    try:
        from codomyrmex.agents.core import AgentRequest

        client = _get_client(backend=backend, model=model, timeout=timeout)
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
    description="List all skills available to the Hermes agent (CLI backend only).",
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
        return {"status": "error", "message": result.get("error", "Skills require CLI backend")}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
