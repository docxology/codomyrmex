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

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the feature_flags module."""
    return {
        "list": {
            "help": "List all feature flags",
            "handler": lambda: print(
                "Feature Flags:\n"
                + (
                    "  (FeatureManager available - use FeatureManager.list_flags())"
                    if HAS_FEATURE_MANAGER
                    else "  (FeatureManager not installed)"
                )
            ),
        },
        "toggle": {
            "help": "Toggle a feature flag on or off",
            "args": ["--flag"],
            "handler": lambda flag=None: (
                print(f"Toggling feature flag: {flag}")
                if flag
                else print("Usage: feature_flags toggle --flag <FLAG_NAME>")
            ),
        },
    }


__all__ = [
    "strategies",
    "storage",
    "evaluation",
    "rollout",
    # CLI integration
    "cli_commands",
]

if HAS_FEATURE_MANAGER:
    __all__.append("FeatureManager")

__version__ = "0.1.0"
