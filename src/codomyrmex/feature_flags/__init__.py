"""Feature Flags module for Codomyrmex."""

from .core.manager import FeatureManager

# Submodule exports
from . import core
from . import strategies
from . import storage
from . import evaluation
from . import rollout

__all__ = [
    "FeatureManager",
    "core",
    "strategies",
    "storage",
    "evaluation",
    "rollout",
]

__version__ = "0.1.0"

