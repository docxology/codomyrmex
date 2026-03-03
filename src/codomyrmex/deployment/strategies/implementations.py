"""Concrete deployment strategy implementations."""

from __future__ import annotations

import time
from collections.abc import Callable

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .base import DeploymentStrategy
from .types import DeploymentResult, DeploymentState, DeploymentTarget

logger = get_logger(__name__)


class RollingDeployment(DeploymentStrategy):
    """Rolling deployment - update targets one at a time."""

    def __init__(
        self,
        batch_size: int = 1,
        delay_seconds: float = 0.0,
        health_check: Callable[[DeploymentTarget], bool] | None = None,
    ):
        self.batch_size = batch_size
        self.delay_seconds = delay_seconds
        self.health_check = health_check

    def deploy(
        self,
        targets: list[DeploymentTarget],
        version: str,
        deploy_fn: Callable[[DeploymentTarget, str], bool],
    ) -> DeploymentResult:
        """Deploy."""
        start_time = time.time()
        updated = 0
        failed = 0
        errors = []

        batches = [
            targets[i : i + self.batch_size]
            for i in range(0, len(targets), self.batch_size)
        ]

        for i, batch in enumerate(batches):
            for target in batch:
                try:
                    success = deploy_fn(target, version)

                    if success:
                        target.version = version

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

            if i < len(batches) - 1 and self.delay_seconds > 0:
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
        """Rollback."""
        return self.deploy(targets, previous_version, deploy_fn)


class BlueGreenDeployment(DeploymentStrategy):
    """Blue-green deployment - switch all traffic at once."""

    def __init__(
        self,
        switch_fn: Callable[[str], bool] | None = None,
        health_check: Callable[[DeploymentTarget], bool] | None = None,
    ):
        self.switch_fn = switch_fn
        self.health_check = health_check

    def deploy(
        self,
        targets: list[DeploymentTarget],
        version: str,
        deploy_fn: Callable[[DeploymentTarget, str], bool],
    ) -> DeploymentResult:
        """Deploy."""
        start_time = time.time()
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

        if failed == 0 and updated > 0:
            if self.switch_fn:
                try:
                    if not self.switch_fn(version):
                        errors.append("Traffic switch failed")
                        failed += 1
                except Exception as e:
                    errors.append(f"Switch error: {e}")
                    failed += 1

        return DeploymentResult(
            success=failed == 0,
            targets_updated=updated,
            targets_failed=failed,
            duration_ms=(time.time() - start_time) * 1000,
            state=DeploymentState.COMPLETED if failed == 0 else DeploymentState.FAILED,
            errors=errors,
            metadata={"active_slot": "green" if failed == 0 else "blue"},
        )

    def rollback(
        self,
        targets: list[DeploymentTarget],
        previous_version: str,
        deploy_fn: Callable[[DeploymentTarget, str], bool],
    ) -> DeploymentResult:
        """Rollback."""
        if self.switch_fn:
            self.switch_fn(previous_version)
        return DeploymentResult(
            success=True,
            targets_updated=len(targets),
            targets_failed=0,
            duration_ms=0,
            state=DeploymentState.ROLLED_BACK,
            metadata={"active_slot": "blue"},
        )


class CanaryDeployment(DeploymentStrategy):
    """Canary deployment - gradual rollout with traffic percentage."""

    def __init__(
        self,
        stages: list[float] | None = None,
        stage_duration_seconds: float = 0.0,
        health_check: Callable[[DeploymentTarget], bool] | None = None,
        success_threshold: float = 0.95,
    ):
        self.stages = stages or [10.0, 25.0, 50.0, 100.0]
        self.stage_duration = stage_duration_seconds
        self.health_check = health_check
        self.success_threshold = success_threshold

    def deploy(
        self,
        targets: list[DeploymentTarget],
        version: str,
        deploy_fn: Callable[[DeploymentTarget, str], bool],
    ) -> DeploymentResult:
        """Deploy."""
        start_time = time.time()
        total = len(targets)
        updated = 0
        failed = 0
        errors = []

        for stage_pct in self.stages:
            target_count = int(total * stage_pct / 100)
            targets_to_update = [t for t in targets if t.version != version][
                : target_count - updated
            ]

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

            if (stage_updated + stage_failed) > 0:
                success_rate = stage_updated / (stage_updated + stage_failed)
                if success_rate < self.success_threshold:
                    errors.append(
                        f"Canary failed at {stage_pct}%: success rate {success_rate:.1%}"
                    )
                    return DeploymentResult(
                        success=False,
                        targets_updated=updated,
                        targets_failed=failed,
                        duration_ms=(time.time() - start_time) * 1000,
                        state=DeploymentState.FAILED,
                        errors=errors,
                        metadata={"stopped_at_stage": stage_pct},
                    )

            if stage_pct < 100 and self.stage_duration > 0:
                time.sleep(self.stage_duration)

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
        """Rollback."""
        rolling = RollingDeployment(batch_size=len(targets))
        result = rolling.deploy(targets, previous_version, deploy_fn)
        result.state = DeploymentState.ROLLED_BACK
        return result


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
