"""
Generates pie charts.

- Uses logging_monitoring for logging.
- Recommend calling environment_setup.env_checker.ensure_dependencies_installed() at app startup.
"""

import matplotlib.pyplot as plt

from .plot_utils import apply_theme_to_axes, get_codomyrmex_logger, save_plot

logger = get_codomyrmex_logger(__name__)


def create_pie_chart(
    labels: list,
    sizes: list,
    title: str = "Pie Chart",
    output_path: str = None,
    show_plot: bool = False,
    autopct: str = "%1.1f%%",
    startangle: int = 90,
    explode: list = None,  # e.g., [0, 0.1, 0, 0] to explode the 2nd slice
    theme=None,
):
    """
    Generates a pie chart.
    Uses logging_monitoring for logging.
    """
    logger.debug(f"Generating pie chart titled '{title}'")
    if not labels or not sizes:
        logger.warning(
            "Empty data for labels or sizes in pie chart. No plot generated."
        )
        return None
    if len(labels) != len(sizes):
        logger.warning(
            f"Length mismatch for pie chart: labels ({len(labels)}) vs sizes ({len(sizes)}). Plot not generated."
        )
        return None
    if explode and len(explode) != len(labels):
        logger.warning(
            f"Length mismatch for pie chart explode: labels ({len(labels)}) vs explode ({len(explode)}). Ignoring explode."
        )
        explode = None

    fig, ax = plt.subplots()
    if theme is not None:
        apply_theme_to_axes(ax, theme)
    # Add a check for sum of sizes to avoid division by zero in autopct if all sizes are 0
    if sum(s for s in sizes if isinstance(s, (int, float))) == 0:
        logger.warning(
            f"All sizes are zero for pie chart '{title}'. Plotting with equal segments if labels exist, but percentages might be misleading."
        )
        # Optionally, plot equal segments or skip autopct
        # sizes = [1] * len(labels) # Plot equal segments
        # autopct = None

    ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        autopct=autopct,
        shadow=True,
        startangle=startangle,
    )
    ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title(title)

    plt.tight_layout()

    if output_path:
        save_plot(fig, output_path)

    if show_plot:
        plt.show()
    else:
        plt.close(fig)
    logger.info(f"Pie chart '{title}' generated successfully.")
    return fig


class PieChart:
    """
    Pie chart class wrapper for object-oriented usage.

    Provides a class-based interface around the create_pie_chart function.
    """

    def __init__(
        self,
        labels: list = None,
        sizes: list = None,
        title: str = "Pie Chart",
        autopct: str = "%1.1f%%",
        startangle: int = 90,
        explode: list = None
    ):
        """
        Initialize a pie chart.

        Args:
            labels: Labels for each slice
            sizes: Size/value for each slice
            title: Chart title
            autopct: Format string for percentage display
            startangle: Starting angle for the first slice
            explode: List of offset distances for each slice
        """
        self.labels = labels or []
        self.sizes = sizes or []
        self.title = title
        self.autopct = autopct
        self.startangle = startangle
        self.explode = explode

    def render(self, output_path: str = None, show_plot: bool = False):
        """
        Render the pie chart.

        Args:
            output_path: Optional path to save the chart
            show_plot: Whether to display the plot interactively
        """
        create_pie_chart(
            labels=self.labels,
            sizes=self.sizes,
            title=self.title,
            output_path=output_path,
            show_plot=show_plot,
            autopct=self.autopct,
            startangle=self.startangle,
            explode=self.explode
        )

    def save(self, output_path: str):
        """Save the chart to a file."""
        self.render(output_path=output_path, show_plot=False)

    def show(self):
        """Display the chart interactively."""
        self.render(show_plot=True)


if __name__ == "__main__":
    from pathlib import Path

    output_dir = Path(__file__).parent.parent / "output" / "data_visualization_examples"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("--- Example: Basic Pie Chart ---")
    pie_labels = ["Frogs", "Hogs", "Dogs", "Logs"]
    pie_sizes = [15, 30, 45, 10]
    create_pie_chart(
        labels=pie_labels,
        sizes=pie_sizes,
        title="Sample Pie Chart: Animal Distribution",
        output_path=str(output_dir / "basic_pie_chart.png"),
        show_plot=False,
    )
    logger.info(f"Pie chart example saved to {output_dir / 'basic_pie_chart.png'}")

    logger.info("--- Example: Pie Chart with Exploded Slice ---")
    pie_explode = [0, 0.1, 0, 0]  # Explode the 2nd slice (Hogs)
    create_pie_chart(
        labels=pie_labels,
        sizes=pie_sizes,
        title="Pie Chart with Exploded Slice",
        output_path=str(output_dir / "exploded_pie_chart.png"),
        show_plot=False,
        explode=pie_explode,
    )
    logger.info(f"Pie chart example saved to {output_dir / 'exploded_pie_chart.png'}")

    import logging

    if not get_codomyrmex_logger("").hasHandlers():
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.info(
            "Basic logging configured for direct script execution of pie_chart.py."
        )
