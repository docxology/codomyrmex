"""
Generates scatter plots.

- Uses logging_monitoring for logging.
- Recommend calling environment_setup.env_checker.ensure_dependencies_installed() at app startup.
"""

import matplotlib.pyplot as plt

from .plot_utils import get_codomyrmex_logger, save_plot

logger = get_codomyrmex_logger(__name__)


def create_scatter_plot(
    x_data: list,
    y_data: list,
    title: str = "Scatter Plot",
    x_label: str = "X-axis",
    y_label: str = "Y-axis",
    output_path: str = None,
    show_plot: bool = False,
    dot_size: int = 20,
    dot_color: str = "blue",
    alpha: float = 0.7,
):
    """
    Generates a scatter plot.
    Uses logging_monitoring for logging.
    """
    logger.debug(f"Generating scatter plot titled '{title}'")
    if len(x_data) == 0 or len(y_data) == 0:
        logger.warning("Empty data provided for scatter plot. No plot generated.")
        return
    if len(x_data) != len(y_data):
        logger.warning(
            f"Length mismatch for scatter plot: x_data ({len(x_data)}) vs y_data ({len(y_data)}). Plot not generated."
        )
        return

    fig, ax = plt.subplots()
    ax.scatter(x_data, y_data, s=dot_size, c=dot_color, alpha=alpha)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(True)

    if output_path:
        save_plot(fig, output_path)

    if show_plot:
        plt.show()
    else:
        plt.close(fig)
    logger.info(f"Scatter plot '{title}' generated successfully.")


class ScatterPlot:
    """
    Scatter plot class wrapper for object-oriented usage.
    
    Provides a class-based interface around the create_scatter_plot function.
    """
    
    def __init__(
        self,
        x_data: list = None,
        y_data: list = None,
        title: str = "Scatter Plot",
        x_label: str = "X-axis",
        y_label: str = "Y-axis",
        dot_size: int = 20,
        dot_color: str = "blue",
        alpha: float = 0.7
    ):
        """
        Initialize a scatter plot.
        
        Args:
            x_data: X-axis data points
            y_data: Y-axis data points
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            dot_size: Size of scatter points
            dot_color: Color of scatter points
            alpha: Transparency of points (0-1)
        """
        self.x_data = x_data or []
        self.y_data = y_data or []
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.dot_size = dot_size
        self.dot_color = dot_color
        self.alpha = alpha
    
    def render(self, output_path: str = None, show_plot: bool = False):
        """
        Render the scatter plot.
        
        Args:
            output_path: Optional path to save the chart
            show_plot: Whether to display the plot interactively
        """
        create_scatter_plot(
            x_data=self.x_data,
            y_data=self.y_data,
            title=self.title,
            x_label=self.x_label,
            y_label=self.y_label,
            output_path=output_path,
            show_plot=show_plot,
            dot_size=self.dot_size,
            dot_color=self.dot_color,
            alpha=self.alpha
        )
    
    def save(self, output_path: str):
        """Save the chart to a file."""
        self.render(output_path=output_path, show_plot=False)
    
    def show(self):
        """Display the chart interactively."""
        self.render(show_plot=True)


if __name__ == "__main__":
    # Example Usage
    from pathlib import Path

    output_dir = Path(__file__).parent.parent / "output" / "data_visualization_examples"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("--- Example: Basic Scatter Plot ---")
    sample_x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sample_y = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]  # Prime numbers
    create_scatter_plot(
        x_data=sample_x,
        y_data=sample_y,
        title="Sample Scatter Plot: Prime Numbers",
        x_label="Index",
        y_label="Prime Number",
        output_path=str(output_dir / "basic_scatter_plot.png"),
        show_plot=False,
        dot_color="green",
        alpha=0.6,
    )
    logger.info(
        f"Scatter plot example saved to {output_dir / 'basic_scatter_plot.png'}"
    )

    logger.info("--- Example: Scatter Plot with Different Dot Size ---")
    sample_x_2 = [i * 0.5 for i in range(20)]
    sample_y_2 = [x**2 for x in sample_x_2]
    create_scatter_plot(
        x_data=sample_x_2,
        y_data=sample_y_2,
        title="Scatter Plot: Quadratic Relationship",
        x_label="X Value",
        y_label="X Squared",
        output_path=str(output_dir / "quadratic_scatter_plot.png"),
        show_plot=False,
        dot_size=50,
        dot_color="purple",
    )
    logger.info(
        f"Scatter plot example saved to {output_dir / 'quadratic_scatter_plot.png'}"
    )

    # Setup a root logger for the example script if this is run directly
    # (assuming logging_monitoring.setup_logging would handle this in a full app context)
    import logging

    if not get_codomyrmex_logger(
        ""
    ).hasHandlers():  # Check if root logger is already configured
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.info(
            "Basic logging configured for direct script execution of scatter_plot.py."
        )
