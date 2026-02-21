"""Deployment strategies — abstract base and concrete implementations.

Provides pluggable deployment strategies:
- RollingStrategy: gradual instance-by-instance replacement.
- CanaryStrategy: traffic-splitting with configurable step sizes.
- BlueGreenStrategy: full-environment swap with rollback support.
- FeatureFlagStrategy: deploy behind a feature flag, enable via toggle.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DeploymentState:
    """Tracks the state of a deployment in progress."""

    service: str
    version: str
    strategy: str
    status: str = "pending"  # pending, in_progress, completed, rolled_back, failed
    started_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    traffic_percentage: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> float:
        end = self.completed_at or time.time()
        return end - self.started_at

    def complete(self) -> None:
        self.status = "completed"
        self.completed_at = time.time()
        self.traffic_percentage = 100.0

    def fail(self, reason: str = "") -> None:
        self.status = "failed"
        self.completed_at = time.time()
        self.metadata["failure_reason"] = reason


class DeploymentStrategy(ABC):
    """Abstract base for deployment strategies."""

    @abstractmethod
    def execute(self, service_name: str, version: str) -> DeploymentState:
        """Execute the deployment. Returns the final state."""

    @abstractmethod
    def rollback(self, state: DeploymentState) -> DeploymentState:
        """Roll back a deployment. Returns the rolled-back state."""


class RollingStrategy(DeploymentStrategy):
    """Rolling deployment — replace instances one batch at a time.

    Args:
        batch_size: Number of instances per batch.
        batch_count: Total number of batches.
        pause_seconds: Pause between batches for health checks.
    """

    def __init__(
        self,
        batch_size: int = 1,
        batch_count: int = 4,
        pause_seconds: float = 0.0,
    ) -> None:
        self.batch_size = batch_size
        self.batch_count = batch_count
        self.pause_seconds = pause_seconds

    def execute(self, service_name: str, version: str) -> DeploymentState:
        state = DeploymentState(service=service_name, version=version, strategy="rolling")
        state.status = "in_progress"

        for i in range(1, self.batch_count + 1):
            pct = (i / self.batch_count) * 100
            state.traffic_percentage = pct
            logger.info(
                "Rolling deploy %s:%s — batch %d/%d (%.0f%%)",
                service_name, version, i, self.batch_count, pct,
            )
            if self.pause_seconds > 0:
                time.sleep(self.pause_seconds)

        state.complete()
        return state

    def rollback(self, state: DeploymentState) -> DeploymentState:
        state.status = "rolled_back"
        state.traffic_percentage = 0.0
        state.completed_at = time.time()
        logger.info("Rolled back rolling deploy for %s", state.service)
        return state


class CanaryStrategy(DeploymentStrategy):
    """Canary deployment — shift traffic in configurable steps.

    Args:
        initial_percentage: Starting traffic percentage for canary.
        step: Percentage increment per step.
        max_steps: Maximum number of steps before full rollout.
    """

    def __init__(
        self,
        initial_percentage: int = 10,
        step: int = 20,
        max_steps: int = 5,
    ) -> None:
        self.initial_percentage = initial_percentage
        self.step = step
        self.max_steps = max_steps

    def execute(self, service_name: str, version: str) -> DeploymentState:
        state = DeploymentState(service=service_name, version=version, strategy="canary")
        state.status = "in_progress"
        pct = self.initial_percentage

        for i in range(self.max_steps):
            state.traffic_percentage = min(pct, 100.0)
            logger.info(
                "Canary %s:%s — step %d, traffic %.0f%%",
                service_name, version, i + 1, state.traffic_percentage,
            )
            if pct >= 100:
                break
            pct += self.step

        state.complete()
        return state

    def rollback(self, state: DeploymentState) -> DeploymentState:
        state.status = "rolled_back"
        state.traffic_percentage = 0.0
        state.completed_at = time.time()
        logger.info("Canary rollback for %s — traffic reset to 0%%", state.service)
        return state


class BlueGreenStrategy(DeploymentStrategy):
    """Blue-Green deployment — full environment swap.

    Deploys the new version to the 'green' environment, then swaps traffic.
    Rollback simply swaps back to 'blue'.
    """

    def execute(self, service_name: str, version: str) -> DeploymentState:
        state = DeploymentState(service=service_name, version=version, strategy="blue_green")
        state.status = "in_progress"

        logger.info("Blue-Green: deploying %s:%s to 'green' slot", service_name, version)
        state.metadata["active_slot"] = "green"
        state.traffic_percentage = 0.0

        logger.info("Blue-Green: swapping traffic from 'blue' to 'green'")
        state.traffic_percentage = 100.0
        state.metadata["active_slot"] = "green"

        state.complete()
        return state

    def rollback(self, state: DeploymentState) -> DeploymentState:
        state.status = "rolled_back"
        state.metadata["active_slot"] = "blue"
        state.traffic_percentage = 100.0  # back on blue
        state.completed_at = time.time()
        logger.info("Blue-Green rollback for %s — swapped back to 'blue'", state.service)
        return state


class FeatureFlagStrategy(DeploymentStrategy):
    """Feature-flag deployment — code deployed but disabled until toggled.

    The service is deployed fully but the new functionality is gated
    behind a feature flag. Traffic percentage represents the %
    of users seeing the new feature.
    """

    def __init__(self, flag_name: str = "", initial_rollout: float = 0.0) -> None:
        self.flag_name = flag_name
        self.initial_rollout = initial_rollout

    def execute(self, service_name: str, version: str) -> DeploymentState:
        state = DeploymentState(service=service_name, version=version, strategy="feature_flag")
        state.metadata["flag_name"] = self.flag_name or f"ff_{service_name}_{version}"
        state.traffic_percentage = self.initial_rollout
        state.complete()
        logger.info(
            "Feature-flag deploy %s:%s — flag '%s' at %.0f%%",
            service_name, version, state.metadata["flag_name"], self.initial_rollout,
        )
        return state

    def rollback(self, state: DeploymentState) -> DeploymentState:
        state.traffic_percentage = 0.0
        state.status = "rolled_back"
        state.completed_at = time.time()
        logger.info("Feature-flag rollback: disabled flag '%s'", state.metadata.get("flag_name"))
        return state
