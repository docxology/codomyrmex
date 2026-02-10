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
]
