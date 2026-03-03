"""
Feature Store Exceptions
"""

from codomyrmex.exceptions.base import CodomyrmexError


class FeatureStoreError(CodomyrmexError):
    """Base exception for feature store operations."""

    pass


class FeatureNotFoundError(FeatureStoreError):
    """Raised when a feature definition or value is not found."""

    pass


class FeatureRegistrationError(FeatureStoreError):
    """Raised when feature registration fails."""

    pass


class FeatureValidationError(FeatureStoreError):
    """Raised when feature value validation fails."""

    pass
