"""Deployment manager — orchestrates deployments with history and rollback.

Coordinates deployment strategies, tracks deployment history, and
provides rollback capabilities.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.deployment.strategies.strategies import (
    DeploymentState,
    DeploymentStrategy,
)
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class DeploymentManager:
    """Orchestrates deployments using pluggable strategies.

    Tracks deployment history and supports rollback to the previous state.

    Example::

        from codomyrmex.deployment.strategies.strategies import CanaryStrategy

        mgr = DeploymentManager()
        state = mgr.deploy("api-server", "v2.1.0", CanaryStrategy())
        assert state.status == "completed"
        assert len(mgr.history) == 1
    """

    def __init__(self) -> None:
        self._history: list[DeploymentState] = []
        self._active: dict[str, DeploymentState] = {}

    def deploy(
        self,
        service_name: str,
        version: str,
        strategy: DeploymentStrategy,
    ) -> DeploymentState:
        """Execute a deployment using the given strategy.

        Args:
            service_name: Name of the service to deploy.
            version: Version string to deploy.
            strategy: The deployment strategy to use.

        Returns:
            DeploymentState reflecting the outcome.
        """
        logger.info("Deploying %s:%s using %s", service_name, version, type(strategy).__name__)
        try:
            state = strategy.execute(service_name, version)
            self._history.append(state)
            self._active[service_name] = state
            logger.info("Deployment %s:%s → %s", service_name, version, state.status)
            return state
        except Exception as e:
            state = DeploymentState(
                service=service_name,
                version=version,
                strategy=type(strategy).__name__,
            )
            state.fail(str(e))
            self._history.append(state)
            logger.error("Deployment failed for %s:%s: %s", service_name, version, e)
            return state

    def rollback(self, service_name: str, strategy: DeploymentStrategy) -> DeploymentState | None:
        """Roll back the most recent deployment of a service.

        Args:
            service_name: Name of the service to roll back.
            strategy: The strategy to use for rollback.

        Returns:
            Updated DeploymentState, or None if no active deployment found.
        """
        active = self._active.get(service_name)
        if active is None:
            logger.warning("No active deployment for %s to roll back", service_name)
            return None

        rolled = strategy.rollback(active)
        self._history.append(rolled)
        del self._active[service_name]
        logger.info("Rolled back %s to previous state", service_name)
        return rolled

    def get_active(self, service_name: str) -> DeploymentState | None:
        """Get the current active deployment for a service."""
        return self._active.get(service_name)

    @property
    def history(self) -> list[DeploymentState]:
        """Return the full deployment history."""
        return list(self._history)

    @property
    def active_deployments(self) -> dict[str, DeploymentState]:
        """Return all currently active deployments."""
        return dict(self._active)

    def summary(self) -> dict[str, Any]:
        """Return a summary of deployment activity."""
        return {
            "total_deployments": len(self._history),
            "active_services": list(self._active.keys()),
            "completed": sum(1 for s in self._history if s.status == "completed"),
            "failed": sum(1 for s in self._history if s.status == "failed"),
            "rolled_back": sum(1 for s in self._history if s.status == "rolled_back"),
        }
