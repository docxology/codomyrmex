"""
Model Registry

Model versioning, lifecycle management, and artifact storage.
"""

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .models import (
    ModelFramework,
    ModelMetrics,
    ModelStage,
    ModelVersion,
    RegisteredModel,
)
from .registry import ModelRegistry
from .stores import (
    FileModelStore,
    InMemoryModelStore,
    ModelStore,
)


def cli_commands():
    """Return CLI commands for the model_registry module."""
    return {
        "list": {
            "help": "List registered models",
            "handler": lambda **kwargs: print(
                "Model Registry\n"
                f"  Stages: {', '.join(ms.value if hasattr(ms, 'value') else str(ms) for ms in ModelStage)}\n"
                f"  Frameworks: {', '.join(mf.value if hasattr(mf, 'value') else str(mf) for mf in ModelFramework)}\n"
                "  Stores: FileModelStore, InMemoryModelStore\n"
                "  Use ModelRegistry to list and manage models programmatically."
            ),
        },
        "info": {
            "help": "Show model info (use --name to specify model)",
            "handler": lambda name=None, **kwargs: print(
                f"Model Info: {name or '(no model specified)'}\n"
                "  Use ModelRegistry.get_model(name) for detailed model information.\n"
                "  Available fields: stage, framework, metrics, versions"
            ),
        },
    }


__all__ = [
    # CLI integration
    "cli_commands",
    # Models
    "ModelStage",
    "ModelFramework",
    "ModelMetrics",
    "ModelVersion",
    "RegisteredModel",
    # Stores
    "ModelStore",
    "FileModelStore",
    "InMemoryModelStore",
    # Registry
    "ModelRegistry",
]
