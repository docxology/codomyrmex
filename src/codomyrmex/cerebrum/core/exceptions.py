"""CEREBRUM Module Exception Classes.

This module defines exception classes specific to the CEREBRUM module for
case-based reasoning and Bayesian inference operations.
"""


class CerebrumError(Exception):
    """Base exception for cerebrum module."""


class CaseError(CerebrumError):
    """Base exception for case errors."""


class CaseNotFoundError(CaseError):
    """Exception raised when a case is not found."""


class InvalidCaseError(Exception):
    """Exception raised when a case is invalid."""


class ModelError(Exception):
    """Exception raised when a model operation fails."""


class TransformationError(Exception):
    """Exception raised when a transformation fails."""


class VisualizationError(Exception):
    """Exception raised when a visualization fails."""


class InferenceError(Exception):
    """Exception raised when inference fails."""


class BayesianInferenceError(InferenceError):
    """Exception raised when Bayesian inference fails."""


class NetworkStructureError(Exception):
    """Exception raised when a network structure is invalid."""


class ActiveInferenceError(Exception):
    """Exception raised when active inference fails."""
