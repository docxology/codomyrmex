"""Abstract base class for deployment strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from .types import DeploymentResult, DeploymentTarget


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

    @abstractmethod
    def rollback(
        self,
        targets: list[DeploymentTarget],
        previous_version: str,
        deploy_fn: Callable[[DeploymentTarget, str], bool],
    ) -> DeploymentResult:
        """Rollback to a previous version."""
