"""
Feature Store Exceptions
"""

from codomyrmex.exceptions.base import CodomyrmexError


class FeatureStoreError(CodomyrmexError):
    """Base exception for feature store operations."""


class FeatureNotFoundError(FeatureStoreError):
    """Raised when a feature definition or value is not found."""


class FeatureRegistrationError(FeatureStoreError):
    """Raised when feature registration fails."""


class FeatureValidationError(FeatureStoreError):
    """Raised when feature value validation fails."""
