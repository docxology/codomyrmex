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
    "BlueGreenDeployment",
    "BlueGreenStrategy",
    # Canary analysis
    "CanaryAnalyzer",
    "CanaryDecision",
    "CanaryDeployment",
    "CanaryReport",
    # Aliases for convenience
    "CanaryStrategy",
    # Manager classes
    "DeploymentManager",
    "DeploymentResult",
    # Strategy classes
    "DeploymentState",
    "DeploymentStrategy",
    "DeploymentTarget",
    "GitOpsSynchronizer",
    "MetricComparison",
    "RollingDeployment",
    "RollingStrategy",
    "StrategyProgress",
    "create_strategy",
    # Submodules
    "health_checks",
    "rollback",
    "strategies",
]

__version__ = "0.2.0"
