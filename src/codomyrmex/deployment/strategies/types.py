"""Common types for deployment strategies."""

from __future__ import annotations

import time
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


@dataclass
class StrategyProgress:
    """Tracks the progress of a strategy execution."""

    service: str
    version: str
    strategy_name: str
    status: DeploymentState = DeploymentState.PENDING
    started_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    traffic_percentage: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> float:
        end = self.completed_at or time.time()
        return end - self.started_at

    def complete(self) -> None:
        """Mark as completed."""
        self.status = DeploymentState.COMPLETED
        self.completed_at = time.time()
        self.traffic_percentage = 100.0

    def fail(self, reason: str = "") -> None:
        """Mark as failed."""
        self.status = DeploymentState.FAILED
        self.completed_at = time.time()
        self.metadata["failure_reason"] = reason
