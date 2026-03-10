"""
Main plotter interface for the Data Visualization module.

This module consolidates and exports plotting functions from the charts package.
It acts as the primary entry point for accessing visualization capabilities.
"""

from codomyrmex.data_visualization.utils import DEFAULT_FIGURE_SIZE, save_plot
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class Plotter:
    """Visualization facade providing uniform error handling, logging, and figure-size defaults.

    All methods catch chart-level exceptions, log them with full context, and
    re-raise as ``RuntimeError`` so callers get a consistent exception type
    regardless of which underlying chart library raised the error.
    """

    def __init__(self, figure_size: tuple = DEFAULT_FIGURE_SIZE):
        self.figure_size = figure_size

    def bar_chart(self, categories, values, **kwargs):
        """Create a bar chart."""
        from codomyrmex.data_visualization.charts.bar_chart import create_bar_chart

        kwargs.setdefault("figure_size", self.figure_size)
        try:
            return create_bar_chart(categories, values, **kwargs)
        except Exception as exc:
            logger.error("bar_chart failed: %s", exc, exc_info=True)
            raise RuntimeError(f"bar_chart failed: {exc}") from exc

    def line_plot(self, x_data, y_data, **kwargs):
        """Create a line plot."""
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot

        kwargs.setdefault("figure_size", self.figure_size)
        try:
            return create_line_plot(x_data, y_data, **kwargs)
        except Exception as exc:
            logger.error("line_plot failed: %s", exc, exc_info=True)
            raise RuntimeError(f"line_plot failed: {exc}") from exc

    def scatter_plot(self, x_data, y_data, **kwargs):
        """Create a scatter plot."""
        from codomyrmex.data_visualization.charts.scatter_plot import (
            create_scatter_plot,
        )

        kwargs.setdefault("figure_size", self.figure_size)
        try:
            return create_scatter_plot(x_data, y_data, **kwargs)
        except Exception as exc:
            logger.error("scatter_plot failed: %s", exc, exc_info=True)
            raise RuntimeError(f"scatter_plot failed: {exc}") from exc

    def histogram(self, data, **kwargs):
        """Create a histogram."""
        from codomyrmex.data_visualization.charts.histogram import create_histogram

        kwargs.setdefault("figure_size", self.figure_size)
        try:
            return create_histogram(data, **kwargs)
        except Exception as exc:
            logger.error("histogram failed: %s", exc, exc_info=True)
            raise RuntimeError(f"histogram failed: {exc}") from exc

    def pie_chart(self, labels, sizes, **kwargs):
        """Create a pie chart."""
        from codomyrmex.data_visualization.charts.pie_chart import create_pie_chart

        kwargs.setdefault("figure_size", self.figure_size)
        try:
            return create_pie_chart(labels, sizes, **kwargs)
        except Exception as exc:
            logger.error("pie_chart failed: %s", exc, exc_info=True)
            raise RuntimeError(f"pie_chart failed: {exc}") from exc

    def heatmap(self, data, **kwargs):
        """Create a heatmap."""
        from codomyrmex.data_visualization.charts.heatmap import create_heatmap

        kwargs.setdefault("figure_size", self.figure_size)
        try:
            return create_heatmap(data, **kwargs)
        except Exception as exc:
            logger.error("heatmap failed: %s", exc, exc_info=True)
            raise RuntimeError(f"heatmap failed: {exc}") from exc


__all__ = [
    "Plotter",
    "save_plot",
]
