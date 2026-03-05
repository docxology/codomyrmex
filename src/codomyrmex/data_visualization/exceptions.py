"""Custom exceptions for the data_visualization module."""

from codomyrmex.exceptions import PlottingError, VisualizationError


class DataVisualizationError(VisualizationError):
    """Base exception for data visualization operations."""


class ChartCreationError(PlottingError):
    """Raised when chart creation fails."""


class InvalidDataError(DataVisualizationError):
    """Raised when input data is invalid for the requested visualization."""


class ThemeError(DataVisualizationError):
    """Raised when theme application or lookup fails."""


class MermaidGenerationError(DataVisualizationError):
    """Raised when Mermaid diagram generation fails."""


class GitVisualizationError(DataVisualizationError):
    """Raised when Git visualization operations fail."""


class PlotSaveError(DataVisualizationError):
    """Raised when saving a plot to file fails."""


__all__ = [
    "ChartCreationError",
    "DataVisualizationError",
    "GitVisualizationError",
    "InvalidDataError",
    "MermaidGenerationError",
    "PlotSaveError",
    "ThemeError",
]
