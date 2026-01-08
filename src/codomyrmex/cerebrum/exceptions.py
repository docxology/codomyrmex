
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring import get_logger
"""CEREBRUM Module Exception Classes.

"""Core functionality module

This module provides exceptions functionality including:
- 0 functions: 
- 11 classes: CerebrumError, CaseError, BayesianInferenceError...

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
This module defines exception classes specific to the CEREBRUM module for
case-based reasoning and Bayesian inference operations.
"""



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


class VisualizationError(CerebrumError):
    """Exception raised for visualization errors."""

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



