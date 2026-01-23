"""Deployment module for Codomyrmex."""

from .manager.manager import DeploymentManager
from .strategies.strategies import DeploymentStrategy, CanaryStrategy, BlueGreenStrategy
from .gitops.gitops import GitOpsSynchronizer

# Submodule exports
from . import manager
from . import strategies
from . import gitops
from . import rollback
from . import health_checks

__all__ = [
    "DeploymentManager",
    "DeploymentStrategy",
    "CanaryStrategy",
    "BlueGreenStrategy",
    "GitOpsSynchronizer",
    "manager",
    "strategies",
    "gitops",
    "rollback",
    "health_checks",
]

__version__ = "0.1.0"

