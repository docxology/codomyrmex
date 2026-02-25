from __future__ import annotations

"""
CEREBRUM Exceptions

Errors related to the CEREBRUM cognitive system, cases, and Bayesian inference.
"""

from .base import CodomyrmexError


class CerebrumError(CodomyrmexError):
    """Base exception class for all CEREBRUM-related errors."""
    pass


class CaseError(CerebrumError):
    """Exception raised for case-related errors."""
    pass


class BayesianInferenceError(CerebrumError):
    """Exception raised for Bayesian inference errors."""
    pass


class ActiveInferenceError(CerebrumError):
    """Exception raised for active inference errors."""
    pass


class ModelError(CerebrumError):
    """Exception raised for model-related errors."""
    pass


class TransformationError(CerebrumError):
    """Exception raised for model transformation errors."""
    pass


class CaseNotFoundError(CaseError):
    """Exception raised when a case is not found."""
    pass


class InvalidCaseError(CaseError):
    """Exception raised when a case is invalid."""
    pass


class InferenceError(BayesianInferenceError):
    """Exception raised when inference fails."""
    pass


class NetworkStructureError(BayesianInferenceError):
    """Exception raised when Bayesian network structure is invalid."""
    pass
