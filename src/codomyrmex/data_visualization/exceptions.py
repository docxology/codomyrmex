"""Custom exceptions for the data_visualization module."""

from codomyrmex.exceptions import PlottingError, VisualizationError


class DataVisualizationError(VisualizationError):
    """Base exception for data visualization operations."""
    pass


class ChartCreationError(PlottingError):
    """Raised when chart creation fails."""
    pass


class InvalidDataError(DataVisualizationError):
    """Raised when input data is invalid for the requested visualization."""
    pass


class ThemeError(DataVisualizationError):
    """Raised when theme application or lookup fails."""
    pass


class MermaidGenerationError(DataVisualizationError):
    """Raised when Mermaid diagram generation fails."""
    pass


class GitVisualizationError(DataVisualizationError):
    """Raised when Git visualization operations fail."""
    pass


class PlotSaveError(DataVisualizationError):
    """Raised when saving a plot to file fails."""
    pass


__all__ = [
    "DataVisualizationError",
    "ChartCreationError",
    "InvalidDataError",
    "ThemeError",
    "MermaidGenerationError",
    "GitVisualizationError",
    "PlotSaveError",
]
