"""Edge function deployment strategies.

Supports rolling, blue-green, and canary deployment patterns
for distributing functions across edge nodes.
"""

from .deployment import (
    DeploymentManager,
    DeploymentPlan,
    DeploymentState,
    DeploymentStrategy,
)

__all__ = [
    "DeploymentManager",
    "DeploymentPlan",
    "DeploymentState",
    "DeploymentStrategy",
]
