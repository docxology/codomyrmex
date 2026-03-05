"""MCP tools for deployment operations."""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .manager.manager import DeploymentManager
from .strategies.implementations import create_strategy
from .strategies.types import DeploymentTarget

# Global manager instance for MCP tools
_manager = DeploymentManager()


@mcp_tool(category="deployment")
def deployment_execute(
    service_name: str,
    version: str,
    strategy: str = "rolling",
    targets: list[dict[str, Any]] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Execute a deployment for a service.

    Args:
        service_name: Name of the service to deploy.
        version: Version string to deploy.
        strategy: Deployment strategy name ("rolling", "blue_green", "canary").
        targets: Optional list of target dictionaries with 'id', 'name', 'address'.
        **kwargs: Additional strategy-specific parameters.

    Returns:
        Dictionary containing deployment results.
    """
    strat = create_strategy(strategy, **kwargs)

    deployment_targets = None
    if targets:
        deployment_targets = [
            DeploymentTarget(
                id=t["id"],
                name=t["name"],
                address=t["address"],
                metadata=t.get("metadata", {}),
            )
            for t in targets
        ]

    result = _manager.deploy(service_name, version, strat, deployment_targets)

    output = result.to_dict()
    output["service"] = service_name
    output["version"] = version
    return output


@mcp_tool(category="deployment")
def deployment_list_strategies() -> list[str]:
    """List available deployment strategy names.

    Returns:
        List of strategy names.
    """
    return ["rolling", "blue_green", "canary"]


@mcp_tool(category="deployment")
def deployment_get_history() -> list[dict[str, Any]]:
    """Get the history of all deployment operations.

    Returns:
        List of deployment result dictionaries.
    """
    return [r.to_dict() for r in _manager.history]


__all__ = [
    "deployment_execute",
    "deployment_get_history",
    "deployment_list_strategies",
]
