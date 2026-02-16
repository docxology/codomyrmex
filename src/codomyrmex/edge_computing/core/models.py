"""Edge computing models and data types."""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
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


class EdgeExecutionError(Exception):
    """Error during edge function execution."""
    pass
