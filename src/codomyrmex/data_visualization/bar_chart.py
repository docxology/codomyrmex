"""
Generates bar charts.

- Uses logging_monitoring for logging.
- Recommend calling environment_setup.env_checker.ensure_dependencies_installed() at app startup.
"""

import matplotlib.pyplot as plt
from .plot_utils import save_plot, get_codomyrmex_logger

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
        return
    if len(categories) != len(values):
        logger.warning(
            f"Length mismatch for bar chart: categories ({len(categories)}) vs values ({len(values)}). Plot not generated."
        )
        return

    fig, ax = plt.subplots()
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


if __name__ == "__main__":
    from pathlib import Path

    output_dir = Path(__file__).parent.parent / "output" / "data_visualization_examples"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"--- Example: Vertical Bar Chart ---")
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

    logger.info(f"--- Example: Horizontal Bar Chart ---")
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
