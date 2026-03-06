"""MCP tool definitions for the o1 coding agent module.

Exposes o1 single-turn chat execution as an MCP tool.
All tools lazy-import the underlying client to avoid circular dependencies.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="o1",
    description=(
        "Execute a single-turn query against the o1 API. "
        "Useful for reasoning or code generation specific to o1."
    ),
)
def o1_execute(
    prompt: str,
    timeout: int = 120,
) -> dict[str, Any]:
    """Submit a prompt to o1.

    Args:
        prompt: Natural-language query to run.
        timeout: API timeout in seconds (default 120).

    Returns:
        dict with keys: status, content, error, metadata
    """
    try:
        from codomyrmex.agents.core import AgentRequest
        from codomyrmex.agents.o1.o1_client import O1Client

        client = O1Client(config={"timeout": timeout})
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
