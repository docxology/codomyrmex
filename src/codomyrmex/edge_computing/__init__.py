"""
Edge Computing Module

Edge deployment, IoT gateways, and latency-sensitive patterns.
"""

__version__ = "0.1.0"

from .models import (
    EdgeExecutionError,
    EdgeFunction,
    EdgeNode,
    EdgeNodeStatus,
    SyncState,
)
from .sync import EdgeSynchronizer
from .runtime import EdgeRuntime
from .cluster import EdgeCluster
from .metrics import EdgeMetrics, InvocationRecord
from .deployment import (
    DeploymentManager,
    DeploymentPlan,
    DeploymentState,
    DeploymentStrategy,
)
from .scheduler import EdgeScheduler, ScheduledJob, ScheduleType
from .cache import CacheEntry, EdgeCache
from .health import HealthCheck, HealthMonitor

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
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
    "EdgeNode",
    "EdgeNodeStatus",
    "EdgeFunction",
    "EdgeRuntime",
    "EdgeCluster",
    "EdgeSynchronizer",
    "SyncState",
    "EdgeExecutionError",
    "EdgeMetrics",
    "InvocationRecord",
    # Deployment strategies
    "DeploymentManager",
    "DeploymentPlan",
    "DeploymentState",
    "DeploymentStrategy",
    # Scheduler
    "EdgeScheduler",
    "ScheduledJob",
    "ScheduleType",
    # Cache
    "EdgeCache",
    "CacheEntry",
    # Health monitoring
    "HealthMonitor",
    "HealthCheck",
    "cli_commands",
]
