"""Contains the create_line_plot function for generating line plots.

- Uses logging_monitoring for logging.
- Recommend calling environment_setup.env_checker.ensure_dependencies_installed() at app startup.
"""

import os

import matplotlib.pyplot as plt

from .plot_utils import (
    DEFAULT_FIGURE_SIZE,
    apply_common_aesthetics,
    apply_theme_to_axes,
    get_codomyrmex_logger,
    save_plot,
)
from codomyrmex.model_context_protocol.decorators import mcp_tool

logger = get_codomyrmex_logger(__name__)

@mcp_tool()
def create_line_plot(
    x_data: list,
    y_data: list,
    title: str = "Line Plot",
    x_label: str = "X-axis",
    y_label: str = "Y-axis",
    output_path: str = None,
    show_plot: bool = False,
    line_labels: list = None,  # For multiple lines
    markers: bool = False,
    figure_size: tuple = DEFAULT_FIGURE_SIZE,
    theme=None,
):
    """
    Generates a line plot.
    Uses logging_monitoring for logging.
    If y_data is a list of lists, and x_data is a single list, multiple lines are plotted.
    If line_labels are provided, they will be used for the legend.
    """
    logger.debug(f"Generating line plot titled '{title}'")
    if len(x_data) == 0 or len(y_data) == 0:
        logger.warning("Empty data provided for line plot. No plot generated.")
        return None

    fig, ax = plt.subplots(figsize=figure_size)
    if theme is not None:
        apply_theme_to_axes(ax, theme)

    if isinstance(y_data[0], list):  # Multiple lines
        if not line_labels or len(line_labels) != len(y_data):
            line_labels = [f"Line {i+1}" for i in range(len(y_data))]
            logger.debug(
                "Line labels not provided or mismatch length; auto-generating labels."
            )
        for i, y_series in enumerate(y_data):
            if len(x_data) != len(y_series):
                logger.warning(
                    f"Length mismatch for line {line_labels[i]}: x_data ({len(x_data)}) and y_series ({len(y_series)}). Skipping this line."
                )
                continue
            ax.plot(
                x_data, y_series, label=line_labels[i], marker="o" if markers else None
            )
        ax.legend()
    else:  # Single line
        if len(x_data) != len(y_data):
            logger.warning(
                f"Length mismatch: x_data ({len(x_data)}) and y_data ({len(y_data)}). Line plot not generated."
            )
            return None
        ax.plot(x_data, y_data, marker="o" if markers else None)

    apply_common_aesthetics(ax, title, x_label, y_label)
    plt.tight_layout()

    if output_path:
        save_plot(fig, output_path)

    if show_plot:
        logger.debug(f"Displaying plot: {title}")
        plt.show()
    else:
        plt.close(fig)  # Close the figure to free memory if not shown

    logger.info(f"Line plot '{title}' generated successfully.")
    return fig  # Return the figure object for potential further manipulation


class LinePlot:
    """
    Line plot class wrapper for object-oriented usage.

    Provides a class-based interface around the create_line_plot function.
    """

    def __init__(
        self,
        x_data: list = None,
        y_data: list = None,
        title: str = "Line Plot",
        x_label: str = "X-axis",
        y_label: str = "Y-axis",
        line_labels: list = None,
        markers: bool = False,
        figure_size: tuple = None
    ):
        """
        Initialize a line plot.

        Args:
            x_data: X-axis data points
            y_data: Y-axis data points (can be list of lists for multiple lines)
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            line_labels: Labels for multiple lines
            markers: Whether to show markers on data points
            figure_size: Figure dimensions (width, height)
        """
        self.x_data = x_data or []
        self.y_data = y_data or []
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.line_labels = line_labels
        self.markers = markers
        self.figure_size = figure_size or DEFAULT_FIGURE_SIZE

    def render(self, output_path: str = None, show_plot: bool = False):
        """
        Render the line plot.

        Args:
            output_path: Optional path to save the chart
            show_plot: Whether to display the plot interactively
        """
        return create_line_plot(
            x_data=self.x_data,
            y_data=self.y_data,
            title=self.title,
            x_label=self.x_label,
            y_label=self.y_label,
            output_path=output_path,
            show_plot=show_plot,
            line_labels=self.line_labels,
            markers=self.markers,
            figure_size=self.figure_size
        )

    def save(self, output_path: str):
        """Save the chart to a file."""
        self.render(output_path=output_path, show_plot=False)

    def show(self):
        """Display the chart interactively."""
        self.render(show_plot=True)


if __name__ == "__main__":
    # This section is for direct testing of line_plot.py
    # Assumes plot_utils.py is in the same directory or Python path is set correctly.

    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_output_dir = os.path.join(current_dir, "test_outputs_data_visualization")
    os.makedirs(test_output_dir, exist_ok=True)
    logger.info(f"Test outputs will be saved in {test_output_dir}")

    x_simple = [1, 2, 3, 4, 5]
    y_simple = [2, 3, 5, 7, 6]
    y_multiple = [[1, 2, 3, 4, 5], [5, 4, 3, 2, 1], [2, 2, 2, 2, 2]]
    line_labels_multiple = ["Ascending", "Descending", "Constant"]

    create_line_plot(
        x_simple,
        y_simple,
        title="Test Simple Line Plot (from line_plot.py)",
        output_path=os.path.join(test_output_dir, "line_plot_simple_standalone.png"),
        markers=True,
    )

    create_line_plot(
        x_simple,
        y_multiple,
        title="Test Multiple Lines Plot (from line_plot.py)",
        line_labels=line_labels_multiple,
        output_path=os.path.join(test_output_dir, "line_plot_multiple_standalone.png"),
    )

    # Example with show_plot (might require GUI environment)
    # create_line_plot(x_simple, y_simple, title="Test Show Line Plot", show_plot=True)

    logger.info(
        f"Completed direct testing of line_plot.py. Check the '{test_output_dir}' directory."
    )
