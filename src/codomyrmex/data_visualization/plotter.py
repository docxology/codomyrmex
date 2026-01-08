"""
Main plotter interface for the Data Visualization module.

This module consolidates and exports plotting functions from other files within this package.
It acts as the primary entry point for accessing visualization capabilities.

- Uses `logging_monitoring` for logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.
"""

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)
import os

import matplotlib.pyplot as plt
import numpy as np

from .bar_chart import create_bar_chart
from .histogram import create_histogram
from .line_plot import create_line_plot
from .pie_chart import create_pie_chart
from .plot_utils import (
    DEFAULT_FIGURE_SIZE,
    apply_common_aesthetics,
    save_plot,
)
from .scatter_plot import create_scatter_plot

# Attempt to import Codomyrmex logging utilities
try:
    from codomyrmex.logging_monitoring.logger_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    # Fallback to standard logging if Codomyrmex specific logging is not available
    # This might happen if the module is used in isolation or before full project setup.
    logger = logging.getLogger(__name__)
    if not logger.hasHandlers():  # Avoid duplicate handlers if already configured
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    logger.info(
        "Codomyrmex logging_monitoring module not found or not yet configured. Using standard Python logging for data_visualization."
    )

# Recommend: At application startup, call environment_setup.env_checker.ensure_dependencies_installed()
# and logging_monitoring.setup_logging() to ensure dependencies and logging are configured.

# Import performance monitoring
try:
    from codomyrmex.performance import monitor_performance, performance_context

    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    logger.warning("Performance monitoring not available - decorators will be no-op")
    PERFORMANCE_MONITORING_AVAILABLE = False

    # Create no-op decorators
    def monitor_performance(*args, **kwargs):
        """Brief description of monitor_performance.
        
        Args:
        
        
            Returns: Description of return value
        """
"""
        def decorator(func):
    """Brief description of decorator.

Args:
    func : Description of func

    Returns: Description of return value
"""
            return func

        return decorator

    class performance_context:
        """Brief description of performance_context.
        
        This class provides functionality for...
        
        Attributes:
            # Add attribute descriptions here
        
        Methods:
            # Method descriptions will be added automatically
        """
"""
        def __init__(self, *args, **kwargs):
    """Brief description of __init__.

Args:
    self : Description of self

    Returns: Description of return value
"""
            pass

        def __enter__(self):
    """Brief description of __enter__.

Args:
    self : Description of self

    Returns: Description of return value
"""
            return self

        def __exit__(self, *args):
    """Brief description of __exit__.

Args:
    self : Description of self

    Returns: Description of return value
"""
            pass


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
        # Ensure data is numpy array for easier handling of values
        np_data = np.array(data)
        for i in range(np_data.shape[0]):  # y
            for j in range(np_data.shape[1]):  # x
                text_color = "black" if im.norm(np_data[i, j]) > 0.5 else "white"
                ax.text(
                    j,
                    i,
                    format(np_data[i, j], fmt),
                    ha="center",
                    va="center",
                    color=text_color,
                )

    plt.tight_layout()  # Adjust layout

    if output_path:
        save_plot(fig, output_path)  # Uses save_plot from .plot_utils

    if show_plot:
        logger.debug(f"Displaying heatmap: {title}")
        plt.show()
    else:
        plt.close(fig)  # Close the figure to free memory if not shown

    logger.info(f"Heatmap '{title}' generated successfully.")
    return fig


# This section is for direct testing of plotter.py
# Ensure logging is set up if running this file directly for testing
# For project-wide use, setup_logging() from logging_monitoring should be called by the main application.

if __name__ == "__main__":
    # Configure basic logging if running standalone for testing
    # This is a simplified setup; for proper project logging,
    # the main application should call logging_monitoring.setup_logging().
    if not logger.hasHandlers() or all(
        isinstance(h, logging.NullHandler) for h in logger.handlers
    ):
        # If the logger (either codomyrmex or fallback) still has no effective handlers, set up a basic one.
        # This check avoids reconfiguring if the fallback logging.basicConfig already ran or if
        # a parent logger is already configured.
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.info("Configured basic logging for direct plotter.py execution.")

    logger.info("Running plotter.py directly for testing purposes...")

    # Test Data
    x_simple = [1, 2, 3, 4, 5]
    y_simple = [2, 3, 5, 7, 6]
    y_multiple = [[1, 2, 3, 4, 5], [5, 4, 3, 2, 1], [2, 2, 2, 2, 2]]
    line_labels_multiple = ["Ascending", "Descending", "Constant"]
    categories_simple = ["A", "B", "C", "D", "E"]
    values_simple = [10, 24, 15, 30, 22]
    histogram_data_simple = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5]

    # Create a test_outputs directory
    test_output_dir = "test_outputs_data_visualization"
    os.makedirs(test_output_dir, exist_ok=True)
    logger.info(f"Test outputs will be saved in ./{test_output_dir}")

    # Test Bar Chart
    create_bar_chart(
        categories_simple,
        values_simple,
        title="Test Vertical Bar Chart",
        output_path=os.path.join(test_output_dir, "bar_chart_vertical.png"),
    )
    create_bar_chart(
        categories_simple,
        values_simple,
        title="Test Horizontal Bar Chart",
        horizontal=True,
        output_path=os.path.join(test_output_dir, "bar_chart_horizontal.png"),
    )

    # Test Pie Chart
    pie_labels = ["Frogs", "Hogs", "Dogs", "Logs"]
    pie_sizes = [15, 30, 45, 10]
    pie_explode = (0, 0.1, 0, 0)  # explode the 2nd slice (Hogs)
    create_pie_chart(
        pie_labels,
        pie_sizes,
        title="Test Pie Chart",
        explode=pie_explode,
        output_path=os.path.join(test_output_dir, "pie_chart.png"),
    )

    logger.info(
        f"Completed direct testing of plotter.py. Check the '{test_output_dir}' directory for output images."
    )
    # To see plots during testing, you can set show_plot=True, but ensure your environment supports GUI.
    # create_scatter_plot(x_simple, y_simple, title="Test Show Scatter Plot", show_plot=True)

__all__ = [
    "create_line_plot",
    "create_scatter_plot",
    "create_bar_chart",
    "create_histogram",
    "create_pie_chart",
    "create_heatmap",
    "save_plot",
]
