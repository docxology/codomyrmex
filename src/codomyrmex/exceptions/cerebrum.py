"""CEREBRUM Exceptions.

Errors related to the CEREBRUM cognitive system, cases, and Bayesian inference.
"""

from __future__ import annotations

from typing import Any

from .base import CodomyrmexError


class CerebrumError(CodomyrmexError):
    """Base exception class for all CEREBRUM-related errors."""

    def __init__(
        self,
        message: str,
        system_component: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if system_component:
            self.context["system_component"] = system_component


class CaseError(CerebrumError):
    """Exception raised for case-related errors."""

    def __init__(
        self,
        message: str,
        case_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if case_id:
            self.context["case_id"] = case_id


class BayesianInferenceError(CerebrumError):
    """Exception raised for Bayesian inference errors."""

    def __init__(
        self,
        message: str,
        model_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if model_name:
            self.context["model_name"] = model_name


class ActiveInferenceError(CerebrumError):
    """Exception raised for active inference errors."""

    def __init__(
        self,
        message: str,
        agent_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if agent_id:
            self.context["agent_id"] = agent_id


class ModelError(CerebrumError):
    """Exception raised for model-related errors."""

    def __init__(
        self,
        message: str,
        model_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if model_type:
            self.context["model_type"] = model_type


class TransformationError(CerebrumError):
    """Exception raised for model transformation errors."""

    def __init__(
        self,
        message: str,
        source_format: str | None = None,
        target_format: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if source_format:
            self.context["source_format"] = source_format
        if target_format:
            self.context["target_format"] = target_format


class CaseNotFoundError(CaseError):
    """Exception raised when a case is not found."""
    pass


class InvalidCaseError(CaseError):
    """Exception raised when a case is invalid."""

    def __init__(
        self,
        message: str,
        validation_error: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if validation_error:
            self.context["validation_error"] = validation_error


class InferenceError(BayesianInferenceError):
    """Exception raised when inference fails."""

    def __init__(
        self,
        message: str,
        inference_engine: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if inference_engine:
            self.context["inference_engine"] = inference_engine


class NetworkStructureError(BayesianInferenceError):
    """Exception raised when Bayesian network structure is invalid."""

    def __init__(
        self,
        message: str,
        missing_nodes: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if missing_nodes:
            self.context["missing_nodes"] = missing_nodes
