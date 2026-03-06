"""Visualization and Documentation Exceptions.

Errors related to data visualization, plotting, and documentation.
"""

from __future__ import annotations

from typing import Any

from .base import CodomyrmexError


# Visualization Errors
class VisualizationError(CodomyrmexError):
    """Raised when data visualization operations fail.

    Attributes:
        message (str): The error message.
        tool_name (str | None): Name of the visualization tool.
    """

    def __init__(
        self,
        message: str,
        tool_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if tool_name:
            self.context["tool_name"] = tool_name


class PlottingError(VisualizationError):
    """Raised when plotting operations fail.

    Attributes:
        message (str): The error message.
        plot_type (str | None): The type of plot being generated.
    """

    def __init__(
        self,
        message: str,
        plot_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if plot_type:
            self.context["plot_type"] = plot_type


# Documentation Errors
class DocumentationError(CodomyrmexError):
    """Raised when documentation operations fail.

    Attributes:
        message (str): The error message.
        doc_type (str | None): The type of documentation being generated.
    """

    def __init__(
        self,
        message: str,
        doc_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if doc_type:
            self.context["doc_type"] = doc_type


class APIDocumentationError(DocumentationError):
    """Raised when API documentation generation fails.

    Attributes:
        message (str): The error message.
        target_path (str | None): Path where documentation was supposed to be generated.
    """

    def __init__(
        self,
        message: str,
        target_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if target_path:
            self.context["target_path"] = target_path
