"""
Generates bar charts.

- Uses logging_monitoring for logging.
- Recommend calling environment_setup.env_checker.ensure_dependencies_installed() at app startup.
"""

import matplotlib.pyplot as plt

from .plot_utils import apply_theme_to_axes, get_codomyrmex_logger, save_plot

logger = get_codomyrmex_logger(__name__)


def create_bar_chart(
    categories: list,
    values: list,
    title: str = "Bar Chart",
    x_label: str = "Categories",
    y_label: str = "Values",
    output_path: str = None,
    show_plot: bool = False,
    horizontal: bool = False,
    bar_color: str = "skyblue",
    theme=None,
):
    """
    Generates a bar chart (vertical or horizontal).
    Uses logging_monitoring for logging.
    """
    logger.debug(f"Generating bar chart titled '{title}'")
    if not categories or not values:
        logger.warning(
            "Empty data for categories or values in bar chart. No plot generated."
        )
        return None
    if len(categories) != len(values):
        logger.warning(
            f"Length mismatch for bar chart: categories ({len(categories)}) vs values ({len(values)}). Plot not generated."
        )
        return None

    fig, ax = plt.subplots()
    if theme is not None:
        apply_theme_to_axes(ax, theme)
    if horizontal:
        ax.barh(categories, values, color=bar_color)
        ax.set_xlabel(y_label)  # Note: y_label becomes the value axis label
        ax.set_ylabel(x_label)  # x_label becomes the category axis label
    else:
        ax.bar(categories, values, color=bar_color)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

    ax.set_title(title)
    ax.grid(True, axis="y" if not horizontal else "x")

    if not horizontal:
        plt.xticks(rotation=45, ha="right")  # Improve readability of x-axis labels

    plt.tight_layout()  # Adjust layout to prevent labels from being cut off

    if output_path:
        save_plot(fig, output_path)

    if show_plot:
        plt.show()
    else:
        plt.close(fig)
    logger.info(f"Bar chart '{title}' generated successfully.")
    return fig


class BarChart:
    """
    Bar chart class wrapper for object-oriented usage.
    
    Provides a class-based interface around the create_bar_chart function.
    """
    
    def __init__(
        self,
        categories: list = None,
        values: list = None,
        title: str = "Bar Chart",
        x_label: str = "Categories",
        y_label: str = "Values",
        horizontal: bool = False,
        bar_color: str = "skyblue"
    ):
        """
        Initialize a bar chart.
        
        Args:
            categories: List of category labels
            values: List of values for each category
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            horizontal: Whether to create horizontal bars
            bar_color: Color for the bars
        """
        self.categories = categories or []
        self.values = values or []
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.horizontal = horizontal
        self.bar_color = bar_color
    
    def render(self, output_path: str = None, show_plot: bool = False):
        """
        Render the bar chart.
        
        Args:
            output_path: Optional path to save the chart
            show_plot: Whether to display the plot interactively
        """
        create_bar_chart(
            categories=self.categories,
            values=self.values,
            title=self.title,
            x_label=self.x_label,
            y_label=self.y_label,
            output_path=output_path,
            show_plot=show_plot,
            horizontal=self.horizontal,
            bar_color=self.bar_color
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

    logger.info("--- Example: Vertical Bar Chart ---")
    sample_categories = ["A", "B", "C", "D", "E"]
    sample_values = [10, 24, 15, 30, 22]
    create_bar_chart(
        categories=sample_categories,
        values=sample_values,
        title="Sample Vertical Bar Chart",
        x_label="Category",
        y_label="Quantity",
        output_path=str(output_dir / "vertical_bar_chart.png"),
        show_plot=False,
        bar_color="lightcoral",
    )
    logger.info(
        f"Vertical bar chart example saved to {output_dir / 'vertical_bar_chart.png'}"
    )

    logger.info("--- Example: Horizontal Bar Chart ---")
    create_bar_chart(
        categories=sample_categories,
        values=sample_values,
        title="Sample Horizontal Bar Chart",
        x_label="Quantity",  # Note: for horizontal, this is the value axis
        y_label="Category",  # Note: for horizontal, this is the category axis
        output_path=str(output_dir / "horizontal_bar_chart.png"),
        show_plot=False,
        horizontal=True,
        bar_color="mediumseagreen",
    )
    logger.info(
        f"Horizontal bar chart example saved to {output_dir / 'horizontal_bar_chart.png'}"
    )

    import logging

    if not get_codomyrmex_logger("").hasHandlers():
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.info(
            "Basic logging configured for direct script execution of bar_chart.py."
        )
