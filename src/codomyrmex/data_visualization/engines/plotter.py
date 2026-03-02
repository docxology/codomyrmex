"""
Main plotter interface for the Data Visualization module.

This module consolidates and exports plotting functions from the charts package.
It acts as the primary entry point for accessing visualization capabilities.
"""

import logging

import matplotlib.pyplot as plt
import numpy as np

from codomyrmex.data_visualization.charts.bar_chart import create_bar_chart
from codomyrmex.data_visualization.charts.histogram import create_histogram
from codomyrmex.data_visualization.charts.line_plot import create_line_plot
from codomyrmex.data_visualization.charts.pie_chart import create_pie_chart
from codomyrmex.data_visualization.charts.plot_utils import (
    DEFAULT_FIGURE_SIZE,
    apply_common_aesthetics,
    save_plot,
)
from codomyrmex.data_visualization.charts.scatter_plot import create_scatter_plot

# Attempt to import Codomyrmex logging utilities
try:
    from codomyrmex.logging_monitoring.core.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)
    if not logger.hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

# Import performance monitoring
try:
    from codomyrmex.performance import monitor_performance, performance_context
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    logger.debug("Performance monitoring not available - decorators will be no-op")
    PERFORMANCE_MONITORING_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        """Decorator for performance monitoring (fallback)."""
        def decorator(func):
            """Decorator."""
            return func
        return decorator

    class performance_context:
        """Performance Context (fallback)."""
        def __init__(self, *args, **kwargs):
            return None  # Intentional no-op
        def __enter__(self):
            """Enter the context manager."""
            return self
        def __exit__(self, *args):
            """Exit the context manager and clean up."""
            return None  # Intentional no-op


class Plotter:
    """Simple wrapper around chart functions providing a unified plotting interface."""

    def __init__(self, figure_size: tuple = DEFAULT_FIGURE_SIZE):
        self.figure_size = figure_size

    def bar_chart(self, categories, values, **kwargs):
        """Create a bar chart."""
        return create_bar_chart(categories, values, **kwargs)

    def line_plot(self, x_data, y_data, **kwargs):
        """Create a line plot."""
        kwargs.setdefault("figure_size", self.figure_size)
        return create_line_plot(x_data, y_data, **kwargs)

    def scatter_plot(self, x_data, y_data, **kwargs):
        """Create a scatter plot."""
        return create_scatter_plot(x_data, y_data, **kwargs)

    def histogram(self, data, **kwargs):
        """Create a histogram."""
        return create_histogram(data, **kwargs)

    def pie_chart(self, labels, sizes, **kwargs):
        """Create a pie chart."""
        return create_pie_chart(labels, sizes, **kwargs)

    def heatmap(self, data, **kwargs):
        """Create a heatmap."""
        kwargs.setdefault("figure_size", self.figure_size)
        return create_heatmap(data, **kwargs)


@monitor_performance("data_viz_create_heatmap")
def create_heatmap(
    data: list,
    x_labels: list = None,
    y_labels: list = None,
    title: str = "Heatmap",
    x_label: str = None,
    y_label: str = None,
    cmap: str = "viridis",
    colorbar_label: str = None,
    output_path: str = None,
    show_plot: bool = False,
    annot: bool = False,
    fmt: str = ".2f",
    figure_size: tuple = DEFAULT_FIGURE_SIZE,
):
    """
    Generates a heatmap from a 2D data array.
    Uses Matplotlib for plotting and plot_utils for saving and aesthetics.
    """
    logger.debug(f"Generating heatmap titled '{title}'")
    if not data or not isinstance(data, list) or not isinstance(data[0], list):
        logger.warning(
            "Invalid or empty 2D data provided for heatmap. No plot generated."
        )
        return None

    fig, ax = plt.subplots(figsize=figure_size)
    im = ax.imshow(data, cmap=cmap)

    # Apply common aesthetics (title, labels)
    apply_common_aesthetics(ax, title, x_label, y_label)

    # Set ticks and labels for x and y axes
    if x_labels:
        ax.set_xticks(np.arange(len(x_labels)))
        ax.set_xticklabels(x_labels)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    if y_labels:
        ax.set_yticks(np.arange(len(y_labels)))
        ax.set_yticklabels(y_labels)

    # Add colorbar
    cbar = fig.colorbar(im)
    if colorbar_label:
        cbar.set_label(colorbar_label)

    # Add annotations
    if annot:
        np_data = np.array(data)
        for i in range(np_data.shape[0]):
            for j in range(np_data.shape[1]):
                text_color = "black" if im.norm(np_data[i, j]) > 0.5 else "white"
                ax.text(
                    j, i,
                    format(np_data[i, j], fmt),
                    ha="center", va="center",
                    color=text_color,
                )

    plt.tight_layout()

    if output_path:
        save_plot(fig, output_path)

    if show_plot:
        logger.debug(f"Displaying heatmap: {title}")
        plt.show()
    else:
        plt.close(fig)

    logger.info(f"Heatmap '{title}' generated successfully.")
    return fig


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
