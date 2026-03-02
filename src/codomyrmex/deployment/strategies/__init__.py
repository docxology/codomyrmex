"""
Deployment strategies.

Provides different deployment strategy implementations.
"""

import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DeploymentState(Enum):
    """States of a deployment."""
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
        """Return a dictionary representation of this object."""
        return {
            "success": self.success,
            "targets_updated": self.targets_updated,
            "targets_failed": self.targets_failed,
            "duration_ms": self.duration_ms,
            "state": self.state.value,
            "errors": self.errors,
        }


class DeploymentStrategy(ABC):
    """Abstract base class for deployment strategies."""

    @abstractmethod
    def deploy(
        self,
        targets: list[DeploymentTarget],
        version: str,
        deploy_fn: Callable[[DeploymentTarget, str], bool],
    ) -> DeploymentResult:
        """Deploy a new version to targets."""
        pass

    @abstractmethod
    def rollback(
        self,
        targets: list[DeploymentTarget],
        previous_version: str,
        deploy_fn: Callable[[DeploymentTarget, str], bool],
    ) -> DeploymentResult:
        """Rollback to a previous version."""
        pass


class RollingDeployment(DeploymentStrategy):
    """Rolling deployment - update targets one at a time."""

    def __init__(
        self,
        batch_size: int = 1,
        delay_seconds: float = 5.0,
        health_check: Callable[[DeploymentTarget], bool] | None = None,
    ):
        """Initialize this instance."""
        self.batch_size = batch_size
        self.delay_seconds = delay_seconds
        self.health_check = health_check

    def deploy(
        self,
        targets: list[DeploymentTarget],
        version: str,
        deploy_fn: Callable[[DeploymentTarget, str], bool],
    ) -> DeploymentResult:
        """deploy ."""
        start_time = time.time()
        updated = 0
        failed = 0
        errors = []

        batches = [
            targets[i:i + self.batch_size]
            for i in range(0, len(targets), self.batch_size)
        ]

        for batch in batches:
            for target in batch:
                try:
                    success = deploy_fn(target, version)

                    if success:
                        target.version = version

                        # Run health check if provided
                        if self.health_check:
                            target.healthy = self.health_check(target)
                            if not target.healthy:
                                errors.append(f"Health check failed for {target.id}")
                                failed += 1
                                continue

                        updated += 1
                    else:
                        failed += 1
                        errors.append(f"Deploy failed for {target.id}")

                except Exception as e:
                    failed += 1
                    errors.append(f"Error deploying to {target.id}: {e}")

            # Delay between batches
            if batches.index(batch) < len(batches) - 1:
                time.sleep(self.delay_seconds)

        return DeploymentResult(
            success=failed == 0,
            targets_updated=updated,
            targets_failed=failed,
            duration_ms=(time.time() - start_time) * 1000,
            state=DeploymentState.COMPLETED if failed == 0 else DeploymentState.FAILED,
            errors=errors,
        )

    def rollback(
        self,
        targets: list[DeploymentTarget],
        previous_version: str,
        deploy_fn: Callable[[DeploymentTarget, str], bool],
    ) -> DeploymentResult:
        """rollback ."""
        return self.deploy(targets, previous_version, deploy_fn)


class BlueGreenDeployment(DeploymentStrategy):
    """Blue-green deployment - switch all traffic at once."""

    def __init__(
        self,
        switch_fn: Callable[[str], bool] | None = None,
        health_check: Callable[[DeploymentTarget], bool] | None = None,
    ):
        """Initialize this instance."""
        self.switch_fn = switch_fn
        self.health_check = health_check

    def deploy(
        self,
        targets: list[DeploymentTarget],
        version: str,
        deploy_fn: Callable[[DeploymentTarget, str], bool],
    ) -> DeploymentResult:
        """deploy ."""
        start_time = time.time()

        # Deploy to all targets (green environment)
        updated = 0
        failed = 0
        errors = []

        for target in targets:
            try:
                if deploy_fn(target, version):
                    target.version = version

                    if self.health_check and not self.health_check(target):
                        errors.append(f"Health check failed: {target.id}")
                        failed += 1
                        continue

                    updated += 1
                else:
                    failed += 1
                    errors.append(f"Deploy failed: {target.id}")

            except Exception as e:
                failed += 1
                errors.append(f"Error: {target.id} - {e}")

        # Only switch if all deployments succeeded
        if failed == 0 and updated > 0:
            if self.switch_fn:
                try:
                    if not self.switch_fn(version):
                        errors.append("Traffic switch failed")
                        return DeploymentResult(
                            success=False,
                            targets_updated=updated,
                            targets_failed=failed,
                            duration_ms=(time.time() - start_time) * 1000,
                            state=DeploymentState.FAILED,
                            errors=errors,
                        )
                except Exception as e:
                    errors.append(f"Switch error: {e}")

        return DeploymentResult(
            success=failed == 0,
            targets_updated=updated,
            targets_failed=failed,
            duration_ms=(time.time() - start_time) * 1000,
            state=DeploymentState.COMPLETED if failed == 0 else DeploymentState.FAILED,
            errors=errors,
        )

    def rollback(
        self,
        targets: list[DeploymentTarget],
        previous_version: str,
        deploy_fn: Callable[[DeploymentTarget, str], bool],
    ) -> DeploymentResult:
        """rollback ."""
        # Just switch traffic back to blue
        if self.switch_fn:
            self.switch_fn(previous_version)
        return DeploymentResult(
            success=True,
            targets_updated=len(targets),
            targets_failed=0,
            duration_ms=0,
            state=DeploymentState.ROLLED_BACK,
        )


class CanaryDeployment(DeploymentStrategy):
    """Canary deployment - gradual rollout with traffic percentage."""

    def __init__(
        self,
        stages: list[float] = None,  # percentages: [10, 25, 50, 100]
        stage_duration_seconds: float = 60.0,
        health_check: Callable[[DeploymentTarget], bool] | None = None,
        success_threshold: float = 0.95,
    ):
        """Initialize this instance."""
        self.stages = stages or [10, 25, 50, 100]
        self.stage_duration = stage_duration_seconds
        self.health_check = health_check
        self.success_threshold = success_threshold

    def deploy(
        self,
        targets: list[DeploymentTarget],
        version: str,
        deploy_fn: Callable[[DeploymentTarget, str], bool],
    ) -> DeploymentResult:
        """deploy ."""
        start_time = time.time()
        total = len(targets)
        updated = 0
        failed = 0
        errors = []

        for stage_pct in self.stages:
            target_count = int(total * stage_pct / 100)
            targets_to_update = [
                t for t in targets
                if t.version != version
            ][:target_count - updated]

            stage_updated = 0
            stage_failed = 0

            for target in targets_to_update:
                try:
                    if deploy_fn(target, version):
                        target.version = version

                        if self.health_check and not self.health_check(target):
                            stage_failed += 1
                            errors.append(f"Canary health check failed: {target.id}")
                            continue

                        stage_updated += 1
                    else:
                        stage_failed += 1

                except Exception as e:
                    stage_failed += 1
                    errors.append(f"Error: {e}")

            updated += stage_updated
            failed += stage_failed

            # Check success rate
            if stage_updated > 0:
                success_rate = stage_updated / (stage_updated + stage_failed)
                if success_rate < self.success_threshold:
                    errors.append(f"Canary failed at {stage_pct}%: success rate {success_rate:.1%}")
                    return DeploymentResult(
                        success=False,
                        targets_updated=updated,
                        targets_failed=failed,
                        duration_ms=(time.time() - start_time) * 1000,
                        state=DeploymentState.FAILED,
                        errors=errors,
                        metadata={"stopped_at_stage": stage_pct},
                    )

            # Wait before next stage
            if stage_pct < 100:
                time.sleep(self.stage_duration)

        return DeploymentResult(
            success=True,
            targets_updated=updated,
            targets_failed=failed,
            duration_ms=(time.time() - start_time) * 1000,
            state=DeploymentState.COMPLETED,
            errors=errors,
        )

    def rollback(
        self,
        targets: list[DeploymentTarget],
        previous_version: str,
        deploy_fn: Callable[[DeploymentTarget, str], bool],
    ) -> DeploymentResult:
        """rollback ."""
        # Rolling rollback to canary targets
        rolling = RollingDeployment(batch_size=5)
        return rolling.deploy(targets, previous_version, deploy_fn)


def create_strategy(strategy_type: str, **kwargs) -> DeploymentStrategy:
    """Factory function for deployment strategies."""
    strategies = {
        "rolling": RollingDeployment,
        "blue_green": BlueGreenDeployment,
        "canary": CanaryDeployment,
    }

    strategy_class = strategies.get(strategy_type)
    if not strategy_class:
        raise ValueError(f"Unknown strategy: {strategy_type}")

    return strategy_class(**kwargs)


__all__ = [
    "DeploymentState",
    "DeploymentTarget",
    "DeploymentResult",
    "DeploymentStrategy",
    "RollingDeployment",
    "BlueGreenDeployment",
    "CanaryDeployment",
    "create_strategy",
]
