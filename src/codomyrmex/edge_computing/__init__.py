"""
Edge Computing Module

Edge deployment, IoT gateways, and latency-sensitive patterns.
"""

__version__ = "0.1.0"

from .core import (
    EdgeCluster,
    EdgeExecutionError,
    EdgeFunction,
    EdgeNode,
    EdgeNodeStatus,
    EdgeRuntime,
    SyncState,
)
from .deployment import (
    DeploymentManager,
    DeploymentPlan,
    DeploymentState,
    DeploymentStrategy,
)
from .infrastructure import (
    CacheEntry,
    EdgeCache,
    EdgeMetrics,
    EdgeSynchronizer,
    HealthCheck,
    HealthMonitor,
    InvocationRecord,
)
from .scheduling import EdgeScheduler, ScheduledJob, ScheduleType

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the edge_computing module."""

    def _nodes():
        """List edge nodes."""
        cluster = EdgeCluster()
        nodes = cluster.list_nodes()
        print("Edge Computing Nodes")
        print(f"  Node Statuses: {[s.value for s in EdgeNodeStatus]}")
        print(f"  Registered Nodes: {len(nodes)}")
        for node in nodes:
            print(f"    - {node.node_id} [{node.status.value}]")

    def _deploy(function_name: str = ""):
        """Deploy a function to edge nodes."""
        if not function_name:
            print("Usage: edge_computing deploy --function <function_name>")
            return
        print(f"Deploying function: {function_name}")
        cluster = EdgeCluster()
        nodes = cluster.list_nodes()
        print(f"  Target nodes: {len(nodes)}")
        print(f"  Sync states: {[s.value for s in SyncState]}")

    return {
        "nodes": _nodes,
        "deploy": _deploy,
    }


__all__ = [
    "CacheEntry",
    # Deployment strategies
    "DeploymentManager",
    "DeploymentPlan",
    "DeploymentState",
    "DeploymentStrategy",
    # Cache
    "EdgeCache",
    "EdgeCluster",
    "EdgeExecutionError",
    "EdgeFunction",
    "EdgeMetrics",
    "EdgeNode",
    "EdgeNodeStatus",
    "EdgeRuntime",
    # Scheduler
    "EdgeScheduler",
    "EdgeSynchronizer",
    "HealthCheck",
    # Health monitoring
    "HealthMonitor",
    "InvocationRecord",
    "ScheduleType",
    "ScheduledJob",
    "SyncState",
    "cli_commands",
]
