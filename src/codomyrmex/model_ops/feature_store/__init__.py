"""
Feature Store

Feature management, storage, and serving for ML applications.
"""

from .models import (
    FeatureType,
    ValueType,
    FeatureDefinition,
    FeatureValue,
    FeatureVector,
    FeatureGroup,
    USER_ID_FEATURE,
    TIMESTAMP_FEATURE,
)

from .store import (
    FeatureStore,
    InMemoryFeatureStore,
)

from .service import (
    FeatureTransform,
    FeatureService,
)

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the feature_store module."""
    def _list_features():
        """Execute  List Features operations natively."""
        print(
            "Feature Store\n"
            "  Feature types: " + ", ".join(ft.value for ft in FeatureType) + "\n"
            "  Value types: " + ", ".join(vt.value for vt in ValueType) + "\n"
            "  Built-in features: USER_ID_FEATURE, TIMESTAMP_FEATURE\n"
            "  Use FeatureStore / InMemoryFeatureStore to manage feature storage."
        )

    def _feature_stats():
        """Execute  Feature Stats operations natively."""
        print(
            "Feature Store Stats\n"
            "  Use FeatureService to serve features with transforms.\n"
            "  Use FeatureGroup to organize related features.\n"
            "  Use FeatureVector for point-in-time feature retrieval."
        )

    return {
        "features": _list_features,
        "stats": _feature_stats,
    }


__all__ = [
    # Models
    "FeatureType",
    "ValueType",
    "FeatureDefinition",
    "FeatureValue",
    "FeatureVector",
    "FeatureGroup",
    "USER_ID_FEATURE",
    "TIMESTAMP_FEATURE",
    # Store
    "FeatureStore",
    "InMemoryFeatureStore",
    # Service
    "FeatureTransform",
    "FeatureService",
    # CLI
    "cli_commands",
]
