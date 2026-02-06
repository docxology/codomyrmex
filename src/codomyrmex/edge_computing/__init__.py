"""
Edge Computing Module

Edge deployment, IoT gateways, and latency-sensitive patterns.
"""

__version__ = "0.1.0"

import asyncio
import hashlib
import json
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from collections.abc import Callable


class EdgeNodeStatus(Enum):
    """Status of an edge node."""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    SYNCING = "syncing"


@dataclass
class EdgeNode:
    """An edge computing node."""
    id: str
    name: str
    location: str = ""
    status: EdgeNodeStatus = EdgeNodeStatus.ONLINE
    capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    last_heartbeat: datetime = field(default_factory=datetime.now)


@dataclass
class EdgeFunction:
    """A function deployable to edge."""
    id: str
    name: str
    handler: Callable[..., Any]
    memory_mb: int = 128
    timeout_seconds: int = 30
    environment: dict[str, str] = field(default_factory=dict)


@dataclass
class SyncState:
    """State synchronization data."""
    version: int
    data: dict[str, Any]
    checksum: str
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_data(cls, data: dict[str, Any], version: int) -> "SyncState":
        checksum = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        return cls(version=version, data=data, checksum=checksum)


class EdgeSynchronizer:
    """Synchronize state between edge and cloud."""

    def __init__(self):
        self._local_state: SyncState | None = None
        self._remote_version = 0
        self._pending_changes: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def get_local_state(self) -> SyncState | None:
        return self._local_state

    def update_local(self, data: dict[str, Any]) -> SyncState:
        """Update local state."""
        with self._lock:
            version = (self._local_state.version if self._local_state else 0) + 1
            self._local_state = SyncState.from_data(data, version)
            self._pending_changes.append({
                "type": "update",
                "version": version,
                "data": data,
            })
        return self._local_state

    def apply_remote(self, state: SyncState) -> bool:
        """Apply remote state if newer."""
        with self._lock:
            if not self._local_state or state.version > self._local_state.version:
                self._local_state = state
                self._remote_version = state.version
                return True
        return False

    def get_pending_changes(self) -> list[dict[str, Any]]:
        """Get changes to sync to remote."""
        with self._lock:
            changes = self._pending_changes.copy()
            return changes

    def confirm_sync(self, up_to_version: int) -> None:
        """Confirm changes synced."""
        with self._lock:
            self._pending_changes = [
                c for c in self._pending_changes if c["version"] > up_to_version
            ]


class EdgeRuntime:
    """Runtime for edge function execution."""

    def __init__(self, node: EdgeNode):
        self.node = node
        self._functions: dict[str, EdgeFunction] = {}

    def deploy(self, function: EdgeFunction) -> None:
        """Deploy a function to edge."""
        self._functions[function.id] = function

    def undeploy(self, function_id: str) -> bool:
        """Undeploy a function."""
        if function_id in self._functions:
            del self._functions[function_id]
            return True
        return False

    def invoke(self, function_id: str, *args, **kwargs) -> Any:
        """Invoke an edge function."""
        func = self._functions.get(function_id)
        if not func:
            raise ValueError(f"Function not found: {function_id}")

        start = time.time()
        try:
            result = func.handler(*args, **kwargs)
            elapsed = time.time() - start
            if elapsed > func.timeout_seconds:
                raise TimeoutError(f"Function exceeded timeout: {elapsed}s")
            return result
        except Exception as e:
            raise EdgeExecutionError(f"Edge function failed: {e}") from e

    def list_functions(self) -> list[EdgeFunction]:
        return list(self._functions.values())


class EdgeExecutionError(Exception):
    """Error during edge function execution."""
    pass


class EdgeCluster:
    """Manage a cluster of edge nodes."""

    def __init__(self):
        self._nodes: dict[str, EdgeNode] = {}
        self._runtimes: dict[str, EdgeRuntime] = {}

    def register_node(self, node: EdgeNode) -> None:
        """Register an edge node."""
        self._nodes[node.id] = node
        self._runtimes[node.id] = EdgeRuntime(node)

    def deregister_node(self, node_id: str) -> bool:
        """Deregister a node."""
        if node_id in self._nodes:
            del self._nodes[node_id]
            del self._runtimes[node_id]
            return True
        return False

    def get_node(self, node_id: str) -> EdgeNode | None:
        return self._nodes.get(node_id)

    def get_runtime(self, node_id: str) -> EdgeRuntime | None:
        return self._runtimes.get(node_id)

    def list_nodes(self, status: EdgeNodeStatus | None = None) -> list[EdgeNode]:
        nodes = list(self._nodes.values())
        if status:
            nodes = [n for n in nodes if n.status == status]
        return nodes

    def deploy_to_all(self, function: EdgeFunction) -> int:
        """Deploy function to all nodes."""
        count = 0
        for runtime in self._runtimes.values():
            runtime.deploy(function)
            count += 1
        return count

    def heartbeat(self, node_id: str) -> None:
        """Update node heartbeat."""
        if node_id in self._nodes:
            self._nodes[node_id].last_heartbeat = datetime.now()
            self._nodes[node_id].status = EdgeNodeStatus.ONLINE


__all__ = [
    "EdgeNode",
    "EdgeNodeStatus",
    "EdgeFunction",
    "EdgeRuntime",
    "EdgeCluster",
    "EdgeSynchronizer",
    "SyncState",
    "EdgeExecutionError",
]
