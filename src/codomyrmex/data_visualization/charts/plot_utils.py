"""
Plot Utilities for Codomyrmex Data Visualization.

Provides shared utility functions for chart generation including:
- Logging configuration
- Plot saving with format detection
- Common styling helpers
- Theme integration
"""

import logging
from pathlib import Path

# Try to import from codomyrmex logging, fallback to standard logging
try:
    from codomyrmex.logging_monitoring.core.logger_config import get_logger

    def get_codomyrmex_logger(name: str):
        """Get a configured logger for the given name."""
        return get_logger(name)
except ImportError:
    def get_codomyrmex_logger(name: str):
        """Get a standard Python logger."""
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
        return logger


logger = get_codomyrmex_logger(__name__)

# Default figure size for plots
DEFAULT_FIGURE_SIZE = (10, 6)

# Constants for consistency with engines/plot_utils
DEFAULT_GRID_STYLE = {"visible": True, "linestyle": "--", "alpha": 0.7}
DEFAULT_TITLE_FONTSIZE = 16
DEFAULT_LABEL_FONTSIZE = 12


def apply_common_aesthetics(ax, title: str = None, x_label: str = None, y_label: str = None):
    """
    Apply common aesthetics to a matplotlib axes.

    Args:
        ax: The matplotlib axes to style.
        title: Optional title to set.
        x_label: Optional x-axis label.
        y_label: Optional y-axis label.

    Returns:
        The styled axes object.
    """
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.3)

    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)

    return ax


def save_plot(
    fig,
    output_path: str,
    dpi: int = 150,
    transparent: bool = False,
    bbox_inches: str = 'tight'
) -> bool:
    """
    Save a matplotlib figure to a file.

    Args:
        fig: The matplotlib figure to save.
        output_path: The path where to save the plot.
        dpi: Dots per inch resolution.
        transparent: Whether to make the background transparent.
        bbox_inches: Bounding box control ('tight' recommended).

    Returns:
        True if saved successfully, False otherwise.
    """
    try:
        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Detect format from extension
        suffix = output_path.suffix.lower()
        fmt = suffix[1:] if suffix else 'png'

        # Save the figure
        fig.savefig(
            output_path,
            format=fmt,
            dpi=dpi,
            transparent=transparent,
            bbox_inches=bbox_inches
        )

        logger.info(f"Plot saved successfully to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to save plot to {output_path}: {e}")
        return False


def apply_codomyrmex_style(ax, title: str = None):
    """
    Apply Codomyrmex styling to a matplotlib axes.

    Args:
        ax: The matplotlib axes to style.
        title: Optional title to set.
    """
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.3)

    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')

    return ax


def get_color_palette(n_colors: int = 10) -> list:
    """
    Get a list of colors for visualizations.

    Args:
        n_colors: Number of colors needed.

    Returns:
        List of color hex codes.
    """
    base_palette = [
        '#1f77b4',  # Blue
        '#ff7f0e',  # Orange
        '#2ca02c',  # Green
        '#d62728',  # Red
        '#9467bd',  # Purple
        '#8c564b',  # Brown
        '#e377c2',  # Pink
        '#7f7f7f',  # Gray
        '#bcbd22',  # Olive
        '#17becf',  # Cyan
    ]

    # Repeat palette if more colors needed
    if n_colors <= len(base_palette):
        return base_palette[:n_colors]
    else:
        repeats = (n_colors // len(base_palette)) + 1
        return (base_palette * repeats)[:n_colors]


def apply_theme_to_axes(ax, theme_name):
    """
    Apply a theme to matplotlib axes.

    Args:
        ax: The matplotlib axes to style.
        theme_name: A ThemeName enum value or string.

    Returns:
        The styled axes object.
    """
    try:
        from codomyrmex.data_visualization.themes import (
            ThemeName,
            apply_theme,
            get_theme,
        )
        if isinstance(theme_name, str):
            theme_name = ThemeName(theme_name)
        theme = get_theme(theme_name)
        apply_theme(theme)
        # Apply axes-specific colors
        ax.set_facecolor(theme.axes_facecolor)
        if ax.figure:
            ax.figure.set_facecolor(theme.figure_facecolor)
    except (ImportError, ValueError) as e:
        logger.debug(f"Could not apply theme: {e}")
    return ax


def configure_plot(fig, ax, theme_name=None, **kwargs):
    """
    Convenience wrapper to configure a plot with optional theme and common settings.

    Args:
        fig: The matplotlib figure.
        ax: The matplotlib axes.
        theme_name: Optional ThemeName enum value or string.
        **kwargs: Additional settings passed to apply_common_aesthetics.

    Returns:
        Tuple of (fig, ax).
    """
    if theme_name is not None:
        apply_theme_to_axes(ax, theme_name)
    apply_common_aesthetics(ax, **kwargs)
    return fig, ax


def apply_style(ax, style_name: str = None):
    """
    Map a style name to a ThemeName and apply it.

    Args:
        ax: The matplotlib axes to style.
        style_name: Style name string (maps to ThemeName values).

    Returns:
        The styled axes object.
    """
    if style_name:
        apply_theme_to_axes(ax, style_name)
    return ax




__all__ = [
    "get_codomyrmex_logger",
    "save_plot",
    "apply_common_aesthetics",
    "apply_codomyrmex_style",
    "get_color_palette",
    "apply_theme_to_axes",
    "configure_plot",
    "apply_style",
    "DEFAULT_FIGURE_SIZE",
    "DEFAULT_GRID_STYLE",
    "DEFAULT_TITLE_FONTSIZE",
    "DEFAULT_LABEL_FONTSIZE",
]
