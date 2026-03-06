"""MCP tool definitions for the codex coding agent module.

Exposes codex single-turn chat execution as an MCP tool.
All tools lazy-import the underlying client to avoid circular dependencies.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="codex",
    description=(
        "Execute a single-turn query against the codex API. "
        "Useful for reasoning or code generation specific to codex."
    ),
)
def codex_execute(
    prompt: str,
    timeout: int = 120,
) -> dict[str, Any]:
    """Submit a prompt to codex.

    Args:
        prompt: Natural-language query to run.
        timeout: API timeout in seconds (default 120).

    Returns:
        dict with keys: status, content, error, metadata
    """
    try:
        from codomyrmex.agents.codex.codex_client import CodexClient
        from codomyrmex.agents.core import AgentRequest

        client = CodexClient(config={"timeout": timeout})
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
