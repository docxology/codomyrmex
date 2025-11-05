"""
Generates histograms.

- Uses logging_monitoring for logging.
- Recommend calling environment_setup.env_checker.ensure_dependencies_installed() at app startup.
"""

import matplotlib.pyplot as plt

from .plot_utils import get_codomyrmex_logger, save_plot

logger = get_codomyrmex_logger(__name__)


def create_histogram(
    data: list,
    bins: int = 10,
    title: str = "Histogram",
    x_label: str = "Value",
    y_label: str = "Frequency",
    output_path: str = None,
    show_plot: bool = False,
    hist_color: str = "cornflowerblue",
    edge_color: str = "black",
):
    """
    Generates a histogram.
    Uses logging_monitoring for logging.
    """
    logger.debug(f"Generating histogram titled '{title}'")
    if not data:
        logger.warning("Empty data provided for histogram. No plot generated.")
        return

    fig, ax = plt.subplots()
    ax.hist(data, bins=bins, color=hist_color, edgecolor=edge_color)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(True, axis="y")

    plt.tight_layout()

    if output_path:
        save_plot(fig, output_path)

    if show_plot:
        plt.show()
    else:
        plt.close(fig)
    logger.info(f"Histogram '{title}' generated successfully.")


if __name__ == "__main__":
    import random
    from pathlib import Path

    output_dir = Path(__file__).parent.parent / "output" / "data_visualization_examples"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("--- Example: Basic Histogram ---")
    # Generate some sample data (e.g., normal distribution)
    random.seed(42)
    sample_data = [random.gauss(0, 1) for _ in range(1000)]
    create_histogram(
        data=sample_data,
        bins=20,
        title="Sample Histogram: Normal Distribution",
        x_label="Value",
        y_label="Frequency",
        output_path=str(output_dir / "basic_histogram.png"),
        show_plot=False,
        hist_color="darkorange",
        edge_color="black",
    )
    logger.info(f"Histogram example saved to {output_dir / 'basic_histogram.png'}")

    logger.info("--- Example: Histogram with Fewer Bins ---")
    sample_data_2 = [random.randint(1, 10) for _ in range(200)]
    create_histogram(
        data=sample_data_2,
        bins=5,
        title="Histogram: Integer Data (Fewer Bins)",
        x_label="Integer Value",
        y_label="Count",
        output_path=str(output_dir / "integer_histogram_fewer_bins.png"),
        show_plot=False,
        hist_color="#FFC300",  # A specific hex color
        edge_color="#581845",  # Darker edge color
    )
    logger.info(
        f"Histogram example saved to {output_dir / 'integer_histogram_fewer_bins.png'}"
    )

    import logging

    if not get_codomyrmex_logger("").hasHandlers():
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.info(
            "Basic logging configured for direct script execution of histogram.py."
        )
