"""MCP tool definitions for the ai_gateway module."""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="ai_gateway",
    description="Route a completion request through the AI Gateway with load balancing and failover.",
)
def gateway_complete(
    prompt: str,
    providers: list[dict[str, Any]] = None,
    strategy: str = "round_robin",
) -> dict[str, Any]:
    """Send a completion request through the AI Gateway.

    Args:
        prompt: The prompt text to complete.
        providers: Optional list of provider configs (name, endpoint, weight).
            If omitted, returns an error asking for provider configuration.
        strategy: Load balancing strategy ('round_robin', 'weighted').

    Returns:
        Dictionary with provider used, response text, latency, and success flag.
    """
    try:
        from .gateway import AIGateway, GatewayConfig, Provider

        if not providers:
            return {
                "status": "error",
                "message": "No providers configured. Supply a list of provider dicts.",
            }

        provider_objs = [
            Provider(
                name=p.get("name", f"provider_{i}"),
                endpoint=p.get("endpoint", ""),
                weight=p.get("weight", 1.0),
            )
            for i, p in enumerate(providers)
        ]

        config = GatewayConfig(strategy=strategy)
        gateway = AIGateway(provider_objs, config)
        result = gateway.complete(prompt)

        return {"status": "success", **result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(
    category="ai_gateway",
    description="Check the health status of all configured AI Gateway providers.",
)
def gateway_health(
    providers: list[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Return health status for all providers.

    Args:
        providers: List of provider configs (name, endpoint).

    Returns:
        Dictionary mapping provider names to their health and circuit state.
    """
    try:
        from .gateway import AIGateway, Provider

        if not providers:
            return {"status": "error", "message": "No providers configured."}

        provider_objs = [
            Provider(
                name=p.get("name", f"provider_{i}"),
                endpoint=p.get("endpoint", ""),
            )
            for i, p in enumerate(providers)
        ]

        gateway = AIGateway(provider_objs)
        health = gateway.health_check()

        return {"status": "success", "providers": health}
    except Exception as e:
        return {"status": "error", "message": str(e)}
