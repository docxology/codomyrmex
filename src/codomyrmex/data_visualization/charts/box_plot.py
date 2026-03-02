"""
Generates box plot visualizations.

Provides both functional and OO interfaces for creating box plots.
"""

import matplotlib.pyplot as plt

from .plot_utils import (
    DEFAULT_FIGURE_SIZE,
    apply_common_aesthetics,
    apply_theme_to_axes,
    get_codomyrmex_logger,
    save_plot,
)

logger = get_codomyrmex_logger(__name__)


def create_box_plot(
    data,
    labels: list = None,
    title: str = "Box Plot",
    x_label: str = None,
    y_label: str = "Values",
    output_path: str = None,
    show_plot: bool = False,
    notch: bool = False,
    patch_artist: bool = True,
    box_color: str = "lightblue",
    figure_size: tuple = DEFAULT_FIGURE_SIZE,
    theme=None,
):
    """
    Generates a box plot.

    Args:
        data: Data for the box plot. Can be:
            - A list of numeric values (single box)
            - A list of lists (multiple boxes)
            - A dict mapping labels to lists of values
        labels: Labels for each box (ignored if data is a dict).
        title: Chart title.
        x_label: X-axis label.
        y_label: Y-axis label.
        output_path: Path to save the plot.
        show_plot: Whether to display the plot.
        notch: Whether to show notches on the boxes.
        patch_artist: Whether to fill boxes with color.
        box_color: Color for the boxes.
        figure_size: Figure dimensions (width, height).
        theme: Optional ThemeName to apply.

    Returns:
        The matplotlib Figure, or None if data is invalid.
    """
    logger.debug(f"Generating box plot titled '{title}'")

    if not data:
        logger.warning("Empty data provided for box plot. No plot generated.")
        return None

    # Normalize data
    if isinstance(data, dict):
        labels = list(data.keys())
        data_list = list(data.values())
    elif isinstance(data, list) and data and isinstance(data[0], list):
        data_list = data
    else:
        data_list = [data]

    if not labels:
        labels = [f"Group {i+1}" for i in range(len(data_list))]

    fig, ax = plt.subplots(figsize=figure_size)

    if theme is not None:
        apply_theme_to_axes(ax, theme)

    bp = ax.boxplot(data_list, labels=labels, notch=notch, patch_artist=patch_artist)

    if patch_artist:
        for patch in bp["boxes"]:
            patch.set_facecolor(box_color)

    apply_common_aesthetics(ax, title, x_label, y_label)
    plt.tight_layout()

    if output_path:
        save_plot(fig, output_path)

    if show_plot:
        plt.show()
    else:
        plt.close(fig)

    logger.info(f"Box plot '{title}' generated successfully.")
    return fig


class BoxPlot:
    """Box plot class wrapper for object-oriented usage."""

    def __init__(
        self,
        data=None,
        labels: list = None,
        title: str = "Box Plot",
        x_label: str = None,
        y_label: str = "Values",
        notch: bool = False,
        patch_artist: bool = True,
        box_color: str = "lightblue",
        figure_size: tuple = None,
        theme=None,
    ):
        """Initialize this instance."""
        self.data = data or []
        self.labels = labels
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.notch = notch
        self.patch_artist = patch_artist
        self.box_color = box_color
        self.figure_size = figure_size or DEFAULT_FIGURE_SIZE
        self.theme = theme

    def render(self, output_path: str = None, show_plot: bool = False):
        """Render the box plot."""
        return create_box_plot(
            data=self.data,
            labels=self.labels,
            title=self.title,
            x_label=self.x_label,
            y_label=self.y_label,
            output_path=output_path,
            show_plot=show_plot,
            notch=self.notch,
            patch_artist=self.patch_artist,
            box_color=self.box_color,
            figure_size=self.figure_size,
            theme=self.theme,
        )

    def save(self, output_path: str):
        """Save the box plot to a file."""
        self.render(output_path=output_path, show_plot=False)

    def show(self):
        """Display the box plot interactively."""
        self.render(show_plot=True)
