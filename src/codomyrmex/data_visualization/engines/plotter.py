"""
Main plotter interface for the Data Visualization module.

This module consolidates and exports plotting functions from the charts package.
It acts as the primary entry point for accessing visualization capabilities.
"""

from codomyrmex.data_visualization.charts.bar_chart import create_bar_chart
from codomyrmex.data_visualization.charts.heatmap import create_heatmap
from codomyrmex.data_visualization.charts.histogram import create_histogram
from codomyrmex.data_visualization.charts.line_plot import create_line_plot
from codomyrmex.data_visualization.charts.pie_chart import create_pie_chart
from codomyrmex.data_visualization.charts.scatter_plot import create_scatter_plot
from codomyrmex.data_visualization.utils import DEFAULT_FIGURE_SIZE, save_plot
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class Plotter:
    """Simple wrapper around chart functions providing a unified plotting interface."""

    def __init__(self, figure_size: tuple = DEFAULT_FIGURE_SIZE):
        self.figure_size = figure_size

    def bar_chart(self, categories, values, **kwargs):
        """Create a bar chart."""
        kwargs.setdefault("figure_size", self.figure_size)
        return create_bar_chart(categories, values, **kwargs)

    def line_plot(self, x_data, y_data, **kwargs):
        """Create a line plot."""
        kwargs.setdefault("figure_size", self.figure_size)
        return create_line_plot(x_data, y_data, **kwargs)

    def scatter_plot(self, x_data, y_data, **kwargs):
        """Create a scatter plot."""
        kwargs.setdefault("figure_size", self.figure_size)
        return create_scatter_plot(x_data, y_data, **kwargs)

    def histogram(self, data, **kwargs):
        """Create a histogram."""
        kwargs.setdefault("figure_size", self.figure_size)
        return create_histogram(data, **kwargs)

    def pie_chart(self, labels, sizes, **kwargs):
        """Create a pie chart."""
        kwargs.setdefault("figure_size", self.figure_size)
        return create_pie_chart(labels, sizes, **kwargs)

    def heatmap(self, data, **kwargs):
        """Create a heatmap."""
        kwargs.setdefault("figure_size", self.figure_size)
        return create_heatmap(data, **kwargs)



__all__ = [
    "Plotter",
    "create_line_plot",
    "create_scatter_plot",
    "create_bar_chart",
    "create_histogram",
    "create_pie_chart",
    "create_heatmap",
    "save_plot",
]
