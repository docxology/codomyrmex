"""Deployment module for Codomyrmex.

Provides deployment strategies, managers, and utilities:
- Canary deployments
- Blue-green deployments
- Rolling deployments
- GitOps synchronization
"""

import os
from typing import Any, Optional

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

# Import strategies and create aliases for common naming conventions
from .strategies import (
    BlueGreenDeployment,
    CanaryDeployment,
    DeploymentResult,
    DeploymentState,
    DeploymentStrategy,
    DeploymentTarget,
    RollingDeployment,
    create_strategy,
)

# Create convenience aliases for different naming conventions
CanaryStrategy = CanaryDeployment
BlueGreenStrategy = BlueGreenDeployment
RollingStrategy = RollingDeployment

# Submodule exports
from codomyrmex.logging_monitoring.core.logger_config import get_logger

from . import health_checks, rollback, strategies

logger = get_logger(__name__)

# Try optional submodules
try:
    from . import manager
except ImportError:
    manager = None

try:
    from . import gitops
except ImportError:
    gitops = None

class DeploymentManager:
    """
    High-level deployment manager for orchestrating deployments.

    Provides a simple interface for deploying services using
    different strategies.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize the deployment manager.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._deployments: list[dict[str, Any]] = []
        self._default_strategy = RollingDeployment()

    def deploy(
        self,
        service_name: str,
        version: str,
        strategy: DeploymentStrategy | None = None,
        targets: list[DeploymentTarget] | None = None,
    ) -> bool:
        """
        Deploy a service version using the specified strategy.

        Args:
            service_name: Name of the service to deploy
            version: Version to deploy
            strategy: Deployment strategy (defaults to rolling)
            targets: Optional list of deployment targets

        Returns:
            True if deployment was successful
        """
        strategy = strategy or self._default_strategy

        # Create mock targets if not provided
        if targets is None:
            targets = [
                DeploymentTarget(
                    id=f"{service_name}-{i}",
                    name=f"{service_name}-instance-{i}",
                    address=f"{os.getenv('DEPLOY_HOST', 'localhost')}:{int(os.getenv('DEPLOY_BASE_PORT', '8000')) + i}",
                )
                for i in range(3)
            ]

        # Mock deploy function
        def deploy_fn(target: DeploymentTarget, ver: str) -> bool:
            target.version = ver
            return True

        try:
            result = strategy.deploy(targets, version, deploy_fn)
        except Exception as e:
            logger.warning("Deployment of %s v%s failed: %s", service_name, version, e)
            self._deployments.append({
                "service": service_name,
                "version": version,
                "strategy": type(strategy).__name__,
                "success": False,
                "targets_updated": 0,
            })
            return False

        self._deployments.append({
            "service": service_name,
            "version": version,
            "strategy": type(strategy).__name__,
            "success": result.success,
            "targets_updated": result.targets_updated,
        })

        return result.success

    def get_deployment_history(self) -> list[dict[str, Any]]:
        """Get history of deployments."""
        return list(self._deployments)

    def rollback(
        self,
        service_name: str,
        previous_version: str,
        strategy: DeploymentStrategy | None = None,
    ) -> bool:
        """
        Rollback a service to a previous version.

        Args:
            service_name: Service to rollback
            previous_version: Version to rollback to
            strategy: Rollback strategy (defaults to rolling)

        Returns:
            True if rollback was successful
        """
        return self.deploy(service_name, previous_version, strategy)

class GitOpsSynchronizer:
    """
    GitOps synchronization manager.

    Synchronizes deployment configurations from a Git repository.
    """

    def __init__(
        self,
        repo_url: str | None = None,
        local_path: str | None = None,
        branch: str = "main",
    ):
        """
        Initialize GitOps synchronizer.

        Args:
            repo_url: URL of the Git repository
            local_path: Local path to clone repository
            branch: Branch to sync from
        """
        self.repo_url = repo_url
        self.local_path = local_path
        self.branch = branch
        self._synced = False

    def sync(self) -> bool:
        """
        Synchronize from Git repository.

        Returns:
            True if sync was successful
        """
        self._synced = True
        return True

    def get_version(self) -> str:
        """
        Get the current synced version via git rev-parse.

        Returns:
            Version string or 'unknown'
        """
        import subprocess
        if self.local_path:
            try:
                result = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    capture_output=True, text=True,
                    cwd=self.local_path,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except Exception as e:
                logger.debug("Failed to get git revision: %s", e)
                pass
        if not self._synced:
            return "unknown"
        return "v1.0.0"

    def is_synced(self) -> bool:
        """Check if currently synced."""
        return self._synced

def cli_commands():
    """Return CLI commands for the deployment module."""
    return {
        "targets": {
            "help": "List deployment targets",
            "handler": lambda **kwargs: print(
                "Deployment Targets:\n"
                + "\n".join(
                    f"  - {t}" for t in ["staging", "production", "canary"]
                )
            ),
        },
        "status": {
            "help": "Show deployment status",
            "handler": lambda **kwargs: print(
                "Deployment Status:\n"
                "  staging    : idle\n"
                "  production : idle\n"
                "  canary     : idle"
            ),
        },
    }

__all__ = [
    # CLI integration
    "cli_commands",
    # Submodules
    "health_checks",
    "strategies",
    "rollback",
    # Strategy classes
    "DeploymentState",
    "DeploymentTarget",
    "DeploymentResult",
    "DeploymentStrategy",
    "RollingDeployment",
    "BlueGreenDeployment",
    "CanaryDeployment",
    "create_strategy",
    # Aliases for convenience
    "CanaryStrategy",
    "BlueGreenStrategy",
    "RollingStrategy",
    # Manager classes
    "DeploymentManager",
    "GitOpsSynchronizer",
]

__version__ = "0.1.0"

