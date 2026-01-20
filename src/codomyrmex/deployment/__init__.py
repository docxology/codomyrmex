"""Deployment module for Codomyrmex."""

from .manager import DeploymentManager
from .strategies import DeploymentStrategy, CanaryStrategy, BlueGreenStrategy
from .gitops import GitOpsSynchronizer

__all__ = [
    "DeploymentManager",
    "DeploymentStrategy",
    "CanaryStrategy",
    "BlueGreenStrategy",
    "GitOpsSynchronizer",
]

__version__ = "0.1.0"
