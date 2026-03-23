"""MCP tool definitions for the Perplexity coding agent module.

Exposes Perplexity API single-turn chat execution as an MCP tool.
All tools lazy-import PerplexityClient to avoid circular dependencies.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="perplexity",
    description=(
        "Execute a single-turn query against the Perplexity API. "
        "Useful for search-augmented up-to-date queries."
    ),
)
def perplexity_execute(
    prompt: str,
    timeout: int = 120,
) -> dict[str, Any]:
    """Submit a prompt to Perplexity.

    Args:
        prompt: Natural-language query to run.
        timeout: API timeout in seconds (default 120).

    Returns:
        dict with keys: status, content, error, metadata
    """
    try:
        from codomyrmex.agents.core import AgentRequest
        from codomyrmex.agents.perplexity.perplexity_client import PerplexityClient

        client = PerplexityClient(config={"timeout": timeout})
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
    category="perplexity",
    description=(
        "Engages in a conversation using the Perplexity API. "
        "Accepts an array of messages (each with a role and content) "
        "and returns a completion response from the Perplexity model."
    ),
)
def perplexity_ask(
    messages: list[dict[str, str]],
    timeout: int = 120,
) -> dict[str, Any]:
    """Submit a multi-turn conversation to Perplexity.

    Args:
        messages: List of message dictionaries containing "role" and "content".
        timeout: API timeout in seconds (default 120).

    Returns:
        dict with keys: status, content, error, metadata
    """
    try:
        from codomyrmex.agents.core import AgentRequest
        from codomyrmex.agents.perplexity.perplexity_client import PerplexityClient

        client = PerplexityClient(config={"timeout": timeout})

        # PerplexityClient defaults to a simple prompt if messages aren't provided in context.
        # We pass the messages array explicitly in the request context.
        # We also attempt to extract a prompt string for logging/compatibility.
        prompt = messages[-1]["content"] if messages else ""
        request = AgentRequest(
            prompt=prompt, context={"messages": messages, "model": "sonar"}
        )

        response = client.execute(request)
        return {
            "status": "success" if response.is_success() else "error",
            "content": response.content,
            "error": response.error,
            "metadata": response.metadata,
        }
    except Exception as exc:
        return {"status": "error", "content": "", "error": str(exc), "metadata": {}}
