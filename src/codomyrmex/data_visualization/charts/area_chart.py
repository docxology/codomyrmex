"""
Generates area chart visualizations.

Provides both functional and OO interfaces for creating area charts,
including stacked area charts.
"""

import matplotlib.pyplot as plt

from codomyrmex.data_visualization.utils import (
    DEFAULT_FIGURE_SIZE,
    apply_common_aesthetics,
    apply_theme_to_axes,
    get_color_palette,
    save_plot,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def create_area_chart(
    x_data: list,
    y_data: list,
    title: str = "Area Chart",
    x_label: str = "X-axis",
    y_label: str = "Y-axis",
    output_path: str | None = None,
    show_plot: bool = False,
    labels: list | None = None,
    alpha: float = 0.5,
    stacked: bool = False,
    figure_size: tuple = DEFAULT_FIGURE_SIZE,
    theme=None,
):
    """
    Generates an area chart using fill_between.

    Args:
        x_data: X-axis data points.
        y_data: Y-axis data. Can be a single list or a list of lists for multiple areas.
        title: Chart title.
        x_label: X-axis label.
        y_label: Y-axis label.
        output_path: Path to save the plot.
        show_plot: Whether to display the plot.
        labels: Labels for each area series (for legend).
        alpha: Fill transparency (0-1).
        stacked: Whether to stack the areas.
        figure_size: Figure dimensions (width, height).
        theme: Optional ThemeName to apply.

    Returns:
        The matplotlib Figure, or None if data is invalid.
    """

    if not x_data or not y_data:
        raise ValueError("Empty data provided for area chart. No plot generated.")

    fig, ax = plt.subplots(figsize=figure_size)

    if theme is not None:
        apply_theme_to_axes(ax, theme)

    colors = get_color_palette(10)

    # Determine if single or multiple series
    if y_data and isinstance(y_data[0], list):
        series_list = y_data
        if not labels:
            labels = [f"Series {i + 1}" for i in range(len(series_list))]

        if stacked:
            ax.stackplot(x_data, *series_list, labels=labels, alpha=alpha)
        else:
            for i, series in enumerate(series_list):
                color = colors[i % len(colors)]
                ax.fill_between(
                    x_data, series, alpha=alpha, color=color, label=labels[i]
                )
                ax.plot(x_data, series, color=color)
        ax.legend()
    else:
        color = colors[0]
        label = labels[0] if labels else None
        ax.fill_between(x_data, y_data, alpha=alpha, color=color, label=label)
        ax.plot(x_data, y_data, color=color)
        if label:
            ax.legend()

    apply_common_aesthetics(ax, title, x_label, y_label)
    plt.tight_layout()

    if output_path:
        save_plot(fig, output_path)

    if show_plot:
        plt.show()
    else:
        plt.close(fig)

    logger.info(f"Area chart '{title}' generated successfully.")
    return fig


class AreaChart:
    """Area chart class wrapper for object-oriented usage."""

    def __init__(
        self,
        x_data: list | None = None,
        y_data: list | None = None,
        title: str = "Area Chart",
        x_label: str = "X-axis",
        y_label: str = "Y-axis",
        labels: list | None = None,
        alpha: float = 0.5,
        stacked: bool = False,
        figure_size: tuple | None = None,
        theme=None,
    ):
        self.x_data = x_data or []
        self.y_data = y_data or []
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.labels = labels
        self.alpha = alpha
        self.stacked = stacked
        self.figure_size = figure_size or DEFAULT_FIGURE_SIZE
        self.theme = theme

    def render(self, output_path: str | None = None, show_plot: bool = False):
        """Render the area chart."""
        return create_area_chart(
            x_data=self.x_data,
            y_data=self.y_data,
            title=self.title,
            x_label=self.x_label,
            y_label=self.y_label,
            output_path=output_path,
            show_plot=show_plot,
            labels=self.labels,
            alpha=self.alpha,
            stacked=self.stacked,
            figure_size=self.figure_size,
            theme=self.theme,
        )

    def save(self, output_path: str):
        """Save the area chart to a file."""
        self.render(output_path=output_path, show_plot=False)

    def show(self):
        """Display the area chart interactively."""
        self.render(show_plot=True)
