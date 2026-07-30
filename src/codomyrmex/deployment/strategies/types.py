"""Common types for deployment strategies."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DeploymentState(Enum):
    """Lifecycle states of a deployment."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    PAUSED = "paused"


@dataclass
class DeploymentTarget:
    """A target for deployment (server, pod, etc.)."""

    id: str
    name: str
    address: str
    healthy: bool = True
    version: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DeploymentResult:
    """Result of a deployment operation."""

    success: bool
    targets_updated: int
    targets_failed: int
    duration_ms: float
    state: DeploymentState
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "targets_updated": self.targets_updated,
            "targets_failed": self.targets_failed,
            "duration_ms": self.duration_ms,
            "state": self.state.value,
            "errors": self.errors,
            "metadata": self.metadata,
        }
