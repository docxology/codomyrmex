"""MCP tools for the deployment module.

Exposes deployment execution, strategy listing, and history retrieval.
Uses zero-delay rolling deployments for fast MCP tool responses.
"""

from __future__ import annotations

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs):
        def decorator(fn):
            fn._mcp_tool_meta = kwargs
            return fn
        return decorator


@mcp_tool(
    category="deployment",
    description=(
        "Execute a simulated deployment using the given strategy "
        "(rolling, blue_green, canary). Returns success status and targets updated."
    ),
)
def deployment_execute(
    service_name: str,
    version: str,
    strategy: str = "rolling",
    targets: list[dict] | None = None,
) -> dict:
    """Execute a deployment and return outcome summary."""
    from codomyrmex.deployment import (
        DeploymentManager,
        DeploymentTarget,
        create_strategy,
    )

    # Build target list from dicts
    target_list = targets or [{"id": "default", "name": "default", "address": "localhost"}]
    target_objs = [
        DeploymentTarget(
            id=t.get("id", f"target-{i}"),
            name=t.get("name", f"target-{i}"),
            address=t.get("address", "localhost"),
        )
        for i, t in enumerate(target_list)
    ]

    # Use fast strategy instances (no real waits for MCP tool context)
    fast_kwargs: dict = {"delay_seconds": 0} if strategy == "rolling" else {}
    if strategy == "canary":
        fast_kwargs = {"stages": [100], "stage_duration_seconds": 0}

    strat = create_strategy(strategy, **fast_kwargs)
    mgr = DeploymentManager()
    success = mgr.deploy(
        service_name=service_name,
        version=version,
        strategy=strat,
        targets=target_objs,
    )
    history = mgr.get_deployment_history()
    latest = history[-1] if history else {}
    return {
        "success": success,
        "service": service_name,
        "version": version,
        "strategy": strategy,
        "targets_updated": latest.get("targets_updated", 0),
    }


@mcp_tool(
    category="deployment",
    description="List the available deployment strategy names.",
)
def deployment_list_strategies() -> list[str]:
    """Return available deployment strategy identifiers."""
    return ["rolling", "blue_green", "canary"]


@mcp_tool(
    category="deployment",
    description=(
        "Get the deployment history recorded by a DeploymentManager instance. "
        "Returns a list of history dicts with service, version, strategy, success fields."
    ),
)
def deployment_get_history(service_name: str | None = None) -> list[dict]:
    """Return deployment history, optionally filtered by service name."""
    from codomyrmex.deployment import DeploymentManager

    mgr = DeploymentManager()
    history = mgr.get_deployment_history()
    if service_name:
        history = [h for h in history if h.get("service") == service_name]
    return history
