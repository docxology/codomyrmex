"""Feature Flags module for Codomyrmex."""

# Submodule exports - import first
from . import evaluation, rollout, storage, strategies

# Try optional submodules
try:
    from . import core
except ImportError:
    pass

# Try to import from existing modules, but don't fail if they don't exist
try:
    from .core.manager import FeatureManager
    HAS_FEATURE_MANAGER = True
except ImportError:
    HAS_FEATURE_MANAGER = False
    FeatureManager = None

__all__ = [
    "strategies",
    "storage",
    "evaluation",
    "rollout",
]

if HAS_FEATURE_MANAGER:
    __all__.append("FeatureManager")

__version__ = "0.1.0"
