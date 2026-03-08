"""
Feature Store

Feature management, storage, and serving for ML applications.
"""

import contextlib

from .exceptions import (
    FeatureNotFoundError,
    FeatureRegistrationError,
    FeatureStoreError,
    FeatureValidationError,
)
from .models import (
    TIMESTAMP_FEATURE,
    USER_ID_FEATURE,
    FeatureDefinition,
    FeatureGroup,
    FeatureType,
    FeatureValue,
    FeatureVector,
    ValueType,
)
from .service import (
    FeatureService,
    FeatureTransform,
)
from .store import (
    FeatureStore,
    InMemoryFeatureStore,
)

# Shared schemas for cross-module interop
with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus


def cli_commands():
    """Return CLI commands for the feature_store module."""

    def _list_features():
        print(
            "Feature Store\n"
            "  Feature types: " + ", ".join(ft.value for ft in FeatureType) + "\n"
            "  Value types: " + ", ".join(vt.value for vt in ValueType) + "\n"
            "  Built-in features: USER_ID_FEATURE, TIMESTAMP_FEATURE\n"
            "  Use FeatureStore / InMemoryFeatureStore to manage feature storage."
        )

    def _feature_stats():
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
    "TIMESTAMP_FEATURE",
    "USER_ID_FEATURE",
    "FeatureDefinition",
    "FeatureGroup",
    "FeatureNotFoundError",
    "FeatureRegistrationError",
    "FeatureService",
    # Store
    "FeatureStore",
    # Exceptions
    "FeatureStoreError",
    # Service
    "FeatureTransform",
    # Models
    "FeatureType",
    "FeatureValidationError",
    "FeatureValue",
    "FeatureVector",
    "InMemoryFeatureStore",
    "ValueType",
    # CLI
    "cli_commands",
]
