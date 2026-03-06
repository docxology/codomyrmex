"""MCP tool definitions for the deepseek coding agent module.

Exposes deepseek single-turn chat execution as an MCP tool.
All tools lazy-import the underlying client to avoid circular dependencies.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="deepseek",
    description=(
        "Execute a single-turn query against the deepseek API. "
        "Useful for reasoning or code generation specific to deepseek."
    ),
)
def deepseek_execute(
    prompt: str,
    timeout: int = 120,
) -> dict[str, Any]:
    """Submit a prompt to deepseek.

    Args:
        prompt: Natural-language query to run.
        timeout: API timeout in seconds (default 120).

    Returns:
        dict with keys: status, content, error, metadata
    """
    try:
        from codomyrmex.agents.core import AgentRequest
        from codomyrmex.agents.deepseek.deepseek_client import DeepSeekClient

        client = DeepSeekClient(config={"timeout": timeout})
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
