"""Edge computing models, node management, and function deployment.

Provides:
- EdgeNodeStatus: node lifecycle states
- EdgeNode: node with capabilities, heartbeat, and resource tracking
- EdgeFunction: deployable function with resource constraints
- SyncState: versioned state with checksum integrity
- EdgeDeployment: function-to-node assignment with status
- EdgeExecutionError: error during edge function execution
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone, UTC
from enum import Enum
from typing import Any


class EdgeNodeStatus(Enum):
    """Status of an edge node."""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    SYNCING = "syncing"
    MAINTENANCE = "maintenance"


@dataclass
class ResourceUsage:
    """Resource utilization of an edge node."""
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_max_mb: float = 0.0
    disk_mb: float = 0.0
    active_functions: int = 0

    @property
    def memory_percent(self) -> float:
        if self.memory_max_mb <= 0:
            return 0.0
        return (self.memory_mb / self.memory_max_mb) * 100

    @property
    def is_overloaded(self) -> bool:
        return self.cpu_percent > 90 or self.memory_percent > 90


@dataclass
class EdgeNode:
    """An edge computing node."""
    id: str
    name: str
    location: str = ""
    status: EdgeNodeStatus = EdgeNodeStatus.ONLINE
    capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(UTC))
    resources: ResourceUsage = field(default_factory=ResourceUsage)
    max_functions: int = 10

    def heartbeat(self) -> None:
        """Update the last heartbeat timestamp."""
        self.last_heartbeat = datetime.now(UTC)

    @property
    def seconds_since_heartbeat(self) -> float:
        delta = datetime.now(UTC) - self.last_heartbeat
        return delta.total_seconds()

    @property
    def is_healthy(self) -> bool:
        return self.status == EdgeNodeStatus.ONLINE and self.seconds_since_heartbeat < 60

    def has_capability(self, capability: str) -> bool:
        return capability in self.capabilities

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "healthy": self.is_healthy,
            "seconds_since_heartbeat": round(self.seconds_since_heartbeat, 1),
        }


@dataclass
class EdgeFunction:
    """A function deployable to edge."""
    id: str
    name: str
    handler: Callable[..., Any]
    memory_mb: int = 128
    timeout_seconds: int = 30
    environment: dict[str, str] = field(default_factory=dict)
    required_capabilities: list[str] = field(default_factory=list)

    def can_run_on(self, node: EdgeNode) -> bool:
        """Check if a node has all required capabilities."""
        return all(node.has_capability(c) for c in self.required_capabilities)


@dataclass
class EdgeDeployment:
    """Assignment of a function to a node."""
    function_id: str
    node_id: str
    deployed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    active: bool = True
    invocations: int = 0

    def record_invocation(self) -> None:
        self.invocations += 1


@dataclass
class SyncState:
    """State synchronization data with checksum integrity."""
    version: int
    data: dict[str, Any]
    checksum: str
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def from_data(cls, data: dict[str, Any], version: int) -> SyncState:
        checksum = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        return cls(version=version, data=data, checksum=checksum)

    def verify(self) -> bool:
        """Verify data integrity against the stored checksum."""
        expected = hashlib.md5(json.dumps(self.data, sort_keys=True).encode()).hexdigest()
        return expected == self.checksum


class EdgeExecutionError(Exception):
    """Error during edge function execution."""
    pass
