"""Deployment manager — orchestrates deployments with history and rollback."""

from __future__ import annotations

import os
from typing import Any

from codomyrmex.deployment.strategies import (
    DeploymentResult,
    DeploymentState,
    DeploymentStrategy,
    DeploymentTarget,
    RollingDeployment,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class DeploymentManager:
    """Orchestrates deployments using pluggable strategies.

    Tracks deployment history and supports rollback to the previous state.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the deployment manager."""
        self.config = config or {}
        self._history: list[DeploymentResult] = []
        self._active: dict[str, str] = {}  # service_name -> version
        self._default_strategy = RollingDeployment()

    def deploy(
        self,
        service_name: str,
        version: str,
        strategy: DeploymentStrategy | None = None,
        targets: list[DeploymentTarget] | None = None,
    ) -> DeploymentResult:
        """Execute a deployment using the given strategy.

        Args:
            service_name: Name of the service to deploy.
            version: Version string to deploy.
            strategy: The deployment strategy to use.
            targets: List of deployment targets.

        Returns:
            DeploymentResult reflecting the outcome.
        """
        strategy = strategy or self._default_strategy
        logger.info("Deploying %s:%s using %s", service_name, version, type(strategy).__name__)

        if targets is None:
            targets = [
                DeploymentTarget(
                    id=f"{service_name}-{i}",
                    name=f"{service_name}-instance-{i}",
                    address=f"{os.getenv('DEPLOY_HOST', 'localhost')}:{int(os.getenv('DEPLOY_BASE_PORT', '8000')) + i}",
                )
                for i in range(3)
            ]

        def deploy_fn(target: DeploymentTarget, ver: str) -> bool:
            target.version = ver
            return True

        try:
            result = strategy.deploy(targets, version, deploy_fn)
            self._history.append(result)
            if result.success:
                self._active[service_name] = version
            logger.info("Deployment %s:%s → %s", service_name, version, result.state.value)
            return result
        except Exception as e:
            logger.error("Deployment failed for %s:%s: %s", service_name, version, e)
            result = DeploymentResult(
                success=False,
                targets_updated=0,
                targets_failed=len(targets),
                duration_ms=0,
                state=DeploymentState.FAILED,
                errors=[str(e)],
            )
            self._history.append(result)
            return result

    def rollback(
        self,
        service_name: str,
        previous_version: str,
        strategy: DeploymentStrategy | None = None,
        targets: list[DeploymentTarget] | None = None,
    ) -> DeploymentResult:
        """Roll back a service to a previous version."""
        strategy = strategy or self._default_strategy
        logger.info("Rolling back %s to version %s", service_name, previous_version)

        if targets is None:
            targets = [
                DeploymentTarget(
                    id=f"{service_name}-{i}",
                    name=f"{service_name}-instance-{i}",
                    address=f"{os.getenv('DEPLOY_HOST', 'localhost')}:{int(os.getenv('DEPLOY_BASE_PORT', '8000')) + i}",
                )
                for i in range(3)
            ]

        def deploy_fn(target: DeploymentTarget, ver: str) -> bool:
            target.version = ver
            return True

        result = strategy.rollback(targets, previous_version, deploy_fn)
        self._history.append(result)
        if result.success:
            self._active[service_name] = previous_version
        return result

    def get_active_version(self, service_name: str) -> str | None:
        """Get the current active version for a service."""
        return self._active.get(service_name)

    @property
    def history(self) -> list[DeploymentResult]:
        """Return the full deployment history."""
        return list(self._history)

    def summary(self) -> dict[str, Any]:
        """Return a summary of deployment activity."""
        return {
            "total_deployments": len(self._history),
            "active_services": list(self._active.keys()),
            "completed": sum(1 for r in self._history if r.state == DeploymentState.COMPLETED),
            "failed": sum(1 for r in self._history if r.state == DeploymentState.FAILED),
            "rolled_back": sum(1 for r in self._history if r.state == DeploymentState.ROLLED_BACK),
        }
