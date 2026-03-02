"""Deployment strategies."""

from .base import DeploymentStrategy
from .implementations import (
    BlueGreenDeployment,
    CanaryDeployment,
    RollingDeployment,
    create_strategy,
)
from .types import (
    DeploymentResult,
    DeploymentState,
    DeploymentTarget,
    StrategyProgress,
)

# Aliases for convenience
CanaryStrategy = CanaryDeployment
BlueGreenStrategy = BlueGreenDeployment
RollingStrategy = RollingDeployment

__all__ = [
    "DeploymentState",
    "DeploymentTarget",
    "DeploymentResult",
    "DeploymentStrategy",
    "RollingDeployment",
    "BlueGreenDeployment",
    "CanaryDeployment",
    "create_strategy",
    "StrategyProgress",
    "CanaryStrategy",
    "BlueGreenStrategy",
    "RollingStrategy",
]
