"""Deployment module for Codomyrmex.

Provides deployment strategies, managers, and utilities:
- Canary deployments
- Blue-green deployments
- Rolling deployments
- GitOps synchronization
"""

from . import health_checks, rollback, strategies
from .canary import CanaryAnalyzer, CanaryDecision, CanaryReport, MetricComparison
from .gitops.gitops import GitOpsSynchronizer
from .manager.manager import DeploymentManager
from .strategies import (
    BlueGreenDeployment,
    BlueGreenStrategy,
    CanaryDeployment,
    CanaryStrategy,
    DeploymentResult,
    DeploymentState,
    DeploymentStrategy,
    DeploymentTarget,
    RollingDeployment,
    RollingStrategy,
    StrategyProgress,
    create_strategy,
)

__all__ = [
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
    "StrategyProgress",
    # Aliases for convenience
    "CanaryStrategy",
    "BlueGreenStrategy",
    "RollingStrategy",
    # Manager classes
    "DeploymentManager",
    "GitOpsSynchronizer",
    # Canary analysis
    "CanaryAnalyzer",
    "CanaryDecision",
    "CanaryReport",
    "MetricComparison",
]

__version__ = "0.2.0"
