"""MCP tool definitions for the edge_computing module.

Exposes edge cluster management and health monitoring as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_cluster():
    """Lazy import of EdgeCluster."""
    from codomyrmex.edge_computing.core.cluster import EdgeCluster

    return EdgeCluster()



@mcp_tool(
    category="edge_computing",
    description="Get edge cluster health status including node counts and function deployments.",
)
def edge_computing_cluster_health() -> dict[str, Any]:
    """Get the health summary of an edge computing cluster.

    Returns:
        dict with keys: status, total_nodes, online, draining,
        total_functions, total_invocations
    """
    try:
        cluster = _get_cluster()
        health = cluster.health()
        return {
            "status": "success",
            **health,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="edge_computing",
    description="List available edge node statuses and deployment strategies.",
)
def edge_computing_list_capabilities() -> dict[str, Any]:
    """List available edge node statuses and deployment strategies.

    Returns:
        dict with keys: status, node_statuses, deployment_strategies, schedule_types
    """
    try:
        from codomyrmex.edge_computing.core.models import EdgeNodeStatus
        from codomyrmex.edge_computing.deployment import (
            DeploymentStrategy,
        )
        from codomyrmex.edge_computing.scheduling import ScheduleType

        return {
            "status": "success",
            "node_statuses": [s.value for s in EdgeNodeStatus],
            "deployment_strategies": [s.value for s in DeploymentStrategy],
            "schedule_types": [s.value for s in ScheduleType],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="edge_computing",
    description="Check health of edge nodes and get recovery recommendations.",
)
def edge_computing_health_check(
    heartbeat_timeout_seconds: float = 60.0,
) -> dict[str, Any]:
    """Run a health check on the monitoring subsystem.

    Args:
        heartbeat_timeout_seconds: Seconds before a node is considered stale.

    Returns:
        dict with keys: status, monitored_nodes, total_checks, timeout_seconds
    """
    try:
        from codomyrmex.edge_computing.infrastructure.health import HealthMonitor

        monitor = HealthMonitor(heartbeat_timeout_seconds=heartbeat_timeout_seconds)
        summary = monitor.summary()
        return {
            "status": "success",
            **summary,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
