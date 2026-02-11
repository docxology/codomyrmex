from __future__ import annotations
"""
Visualization and Documentation Exceptions

Errors related to data visualization, plotting, and documentation.
"""

from .base import CodomyrmexError


# Visualization Errors
class VisualizationError(CodomyrmexError):
    """Raised when data visualization operations fail."""
    pass


class PlottingError(CodomyrmexError):
    """Raised when plotting operations fail."""
    pass


# Documentation Errors
class DocumentationError(CodomyrmexError):
    """Raised when documentation operations fail."""
    pass


class APIDocumentationError(CodomyrmexError):
    """Raised when API documentation generation fails."""
    pass
