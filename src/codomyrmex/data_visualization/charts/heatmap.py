"""
Generates heatmap visualizations.

Provides both functional and OO interfaces for creating heatmaps.
"""

import matplotlib.pyplot as plt
import numpy as np

from .plot_utils import (
    DEFAULT_FIGURE_SIZE,
    apply_common_aesthetics,
    apply_theme_to_axes,
    get_codomyrmex_logger,
    save_plot,
)

logger = get_codomyrmex_logger(__name__)


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
    theme=None,
):
    """
    Generates a heatmap from a 2D data array.

    Args:
        data: 2D list of numeric values.
        x_labels: Labels for x-axis ticks.
        y_labels: Labels for y-axis ticks.
        title: Chart title.
        x_label: X-axis label.
        y_label: Y-axis label.
        cmap: Matplotlib colormap name.
        colorbar_label: Label for the colorbar.
        output_path: Path to save the plot.
        show_plot: Whether to display the plot.
        annot: Whether to annotate cells with values.
        fmt: Format string for annotation values.
        figure_size: Figure dimensions (width, height).
        theme: Optional ThemeName to apply.

    Returns:
        The matplotlib Figure, or None if data is invalid.
    """
    logger.debug(f"Generating heatmap titled '{title}'")
    if not data or not isinstance(data, list) or not isinstance(data[0], list):
        logger.warning("Invalid or empty 2D data provided for heatmap. No plot generated.")
        return None

    fig, ax = plt.subplots(figsize=figure_size)

    if theme is not None:
        apply_theme_to_axes(ax, theme)

    im = ax.imshow(data, cmap=cmap)
    apply_common_aesthetics(ax, title, x_label, y_label)

    if x_labels:
        ax.set_xticks(np.arange(len(x_labels)))
        ax.set_xticklabels(x_labels)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    if y_labels:
        ax.set_yticks(np.arange(len(y_labels)))
        ax.set_yticklabels(y_labels)

    cbar = fig.colorbar(im)
    if colorbar_label:
        cbar.set_label(colorbar_label)

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
        plt.show()
    else:
        plt.close(fig)

    logger.info(f"Heatmap '{title}' generated successfully.")
    return fig


class Heatmap:
    """Heatmap class wrapper for object-oriented usage."""

    def __init__(
        self,
        data: list = None,
        x_labels: list = None,
        y_labels: list = None,
        title: str = "Heatmap",
        x_label: str = None,
        y_label: str = None,
        cmap: str = "viridis",
        colorbar_label: str = None,
        annot: bool = False,
        fmt: str = ".2f",
        figure_size: tuple = None,
        theme=None,
    ):
        """Initialize this instance."""
        self.data = data or []
        self.x_labels = x_labels
        self.y_labels = y_labels
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.cmap = cmap
        self.colorbar_label = colorbar_label
        self.annot = annot
        self.fmt = fmt
        self.figure_size = figure_size or DEFAULT_FIGURE_SIZE
        self.theme = theme

    def render(self, output_path: str = None, show_plot: bool = False):
        """Render the heatmap."""
        return create_heatmap(
            data=self.data,
            x_labels=self.x_labels,
            y_labels=self.y_labels,
            title=self.title,
            x_label=self.x_label,
            y_label=self.y_label,
            cmap=self.cmap,
            colorbar_label=self.colorbar_label,
            output_path=output_path,
            show_plot=show_plot,
            annot=self.annot,
            fmt=self.fmt,
            figure_size=self.figure_size,
            theme=self.theme,
        )

    def save(self, output_path: str):
        """Save the heatmap to a file."""
        self.render(output_path=output_path, show_plot=False)

    def show(self):
        """Display the heatmap interactively."""
        self.render(show_plot=True)
