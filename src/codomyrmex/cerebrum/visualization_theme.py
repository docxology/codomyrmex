"""Professional academic visualization theme system for CEREBRUM.

This module provides a centralized theme system for consistent, publication-quality
visualizations with professional fonts, colorblind-safe palettes, and standardized styling.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

try:
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib import font_manager
    from matplotlib.patches import Patch

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class FontConfig:
    """Font configuration for visualizations."""

    family: str = "sans-serif"
    title_size: float = 18.0
    label_size: float = 12.0
    tick_size: float = 10.0
    legend_size: float = 10.0
    annotation_size: float = 9.0
    weight_title: str = "bold"
    weight_label: str = "normal"
    weight_tick: str = "normal"


@dataclass
class ColorPalette:
    """Colorblind-safe color palette for academic visualizations."""

    # Primary colors (colorblind-safe)
    primary: List[str] = None
    secondary: List[str] = None
    accent: List[str] = None

    # Status colors (semantic)
    stable: str = "#2ecc71"  # Green
    draft: str = "#f39c12"  # Orange
    stub: str = "#95a5a6"  # Gray
    new: str = "#3498db"  # Blue

    # Importance levels
    high: str = "#e74c3c"  # Red
    medium: str = "#f39c12"  # Orange
    low: str = "#95a5a6"  # Gray

    # Network colors
    node_default: str = "#3498db"  # Blue
    edge_default: str = "#7f8c8d"  # Gray
    node_highlight: str = "#e74c3c"  # Red

    def __post_init__(self):
        """Initialize default palettes if not provided."""
        if self.primary is None:
            # ColorBrewer Set2 (colorblind-safe)
            self.primary = [
                "#66c2a5",  # Teal
                "#fc8d62",  # Orange
                "#8da0cb",  # Blue
                "#e78ac3",  # Pink
                "#a6d854",  # Green
                "#ffd92f",  # Yellow
                "#e5c494",  # Tan
                "#b3b3b3",  # Gray
            ]
        if self.secondary is None:
            # ColorBrewer Dark2 (colorblind-safe)
            self.secondary = [
                "#1b9e77",  # Teal
                "#d95f02",  # Orange
                "#7570b3",  # Purple
                "#e7298a",  # Pink
                "#66a61e",  # Green
                "#e6ab02",  # Yellow
                "#a6761d",  # Brown
                "#666666",  # Gray
            ]
        if self.accent is None:
            # Viridis-inspired (colorblind-safe, sequential)
            self.accent = [
                "#440154",  # Dark purple
                "#31688e",  # Blue
                "#35b779",  # Green
                "#6ece58",  # Light green
                "#fde725",  # Yellow
            ]


@dataclass
class FigureConfig:
    """Figure configuration."""

    default_size: Tuple[float, float] = (12.0, 8.0)
    default_dpi: int = 300
    tight_layout_pad: float = 1.5
    save_bbox_inches: str = "tight"
    save_format: str = "png"


@dataclass
class AxisConfig:
    """Axis configuration."""

    grid_alpha: float = 0.3
    grid_linestyle: str = "--"
    grid_linewidth: float = 0.5
    tick_direction: str = "out"
    tick_length: float = 4.0
    tick_width: float = 0.5
    label_pad: float = 8.0
    title_pad: float = 12.0


@dataclass
class LegendConfig:
    """Legend configuration."""

    fontsize: float = 10.0
    frameon: bool = True
    fancybox: bool = True
    shadow: bool = False
    framealpha: float = 0.9
    edgecolor: str = "black"
    facecolor: str = "white"
    loc: str = "best"
    ncol: int = 1
    columnspacing: float = 1.0
    labelspacing: float = 0.5


class VisualizationTheme:
    """Professional academic visualization theme.

    Provides consistent styling for all CEREBRUM visualizations with
    publication-quality defaults.
    """

    def __init__(
        self,
        font_config: Optional[FontConfig] = None,
        color_palette: Optional[ColorPalette] = None,
        figure_config: Optional[FigureConfig] = None,
        axis_config: Optional[AxisConfig] = None,
        legend_config: Optional[LegendConfig] = None,
    ):
        """Initialize theme.

        Args:
            font_config: Font configuration (default: professional academic)
            color_palette: Color palette (default: colorblind-safe)
            figure_config: Figure configuration
            axis_config: Axis configuration
            legend_config: Legend configuration
        """
        self.font = font_config or FontConfig()
        self.colors = color_palette or ColorPalette()
        self.figure = figure_config or FigureConfig()
        self.axis = axis_config or AxisConfig()
        self.legend = legend_config or LegendConfig()

        if HAS_MATPLOTLIB:
            self._setup_matplotlib()

    def _setup_matplotlib(self) -> None:
        """Configure matplotlib with theme settings."""
        try:
            # Set font family
            plt.rcParams["font.family"] = self.font.family
            plt.rcParams["font.sans-serif"] = [
                "Arial",
                "DejaVu Sans",
                "Liberation Sans",
                "Helvetica",
                "sans-serif",
            ]

            # Font sizes
            plt.rcParams["font.size"] = self.font.label_size
            plt.rcParams["axes.titlesize"] = self.font.title_size
            plt.rcParams["axes.labelsize"] = self.font.label_size
            plt.rcParams["xtick.labelsize"] = self.font.tick_size
            plt.rcParams["ytick.labelsize"] = self.font.tick_size
            plt.rcParams["legend.fontsize"] = self.font.legend_size

            # Font weights
            plt.rcParams["axes.titleweight"] = self.font.weight_title
            plt.rcParams["axes.labelweight"] = self.font.weight_label

            # Figure defaults
            plt.rcParams["figure.dpi"] = self.figure.default_dpi
            plt.rcParams["savefig.dpi"] = self.figure.default_dpi
            plt.rcParams["savefig.bbox"] = self.figure.save_bbox_inches
            plt.rcParams["savefig.format"] = self.figure.save_format

            # Grid
            plt.rcParams["grid.alpha"] = self.axis.grid_alpha
            plt.rcParams["grid.linestyle"] = self.axis.grid_linestyle
            plt.rcParams["grid.linewidth"] = self.axis.grid_linewidth

            # Ticks
            plt.rcParams["xtick.direction"] = self.axis.tick_direction
            plt.rcParams["ytick.direction"] = self.axis.tick_direction
            plt.rcParams["xtick.major.size"] = self.axis.tick_length
            plt.rcParams["ytick.major.size"] = self.axis.tick_length
            plt.rcParams["xtick.major.width"] = self.axis.tick_width
            plt.rcParams["ytick.major.width"] = self.axis.tick_width

            # Spacing
            plt.rcParams["axes.labelpad"] = self.axis.label_pad
            plt.rcParams["axes.titlepad"] = self.axis.title_pad

            logger.debug("Matplotlib theme configured")
        except Exception as e:
            logger.warning(f"Failed to configure matplotlib theme: {e}")

    def apply_to_axes(self, ax) -> None:
        """Apply theme to a matplotlib axes object.

        Args:
            ax: Matplotlib axes object
        """
        if not HAS_MATPLOTLIB:
            return

        # Grid
        ax.grid(
            True,
            alpha=self.axis.grid_alpha,
            linestyle=self.axis.grid_linestyle,
            linewidth=self.axis.grid_linewidth,
        )

        # Ticks
        ax.tick_params(
            direction=self.axis.tick_direction,
            length=self.axis.tick_length,
            width=self.axis.tick_width,
        )

    def create_legend(
        self,
        ax,
        handles: List,
        labels: List[str],
        title: Optional[str] = None,
        **kwargs,
    ):
        """Create a styled legend.

        Args:
            ax: Matplotlib axes object
            handles: Legend handles (patches, lines, etc.)
            labels: Legend labels
            title: Optional legend title
            **kwargs: Additional legend parameters

        Returns:
            Legend object
        """
        if not HAS_MATPLOTLIB:
            return None

        legend_params = {
            "fontsize": self.legend.fontsize,
            "frameon": self.legend.frameon,
            "fancybox": self.legend.fancybox,
            "shadow": self.legend.shadow,
            "framealpha": self.legend.framealpha,
            "edgecolor": self.legend.edgecolor,
            "facecolor": self.legend.facecolor,
            "loc": kwargs.pop("loc", self.legend.loc),
            "ncol": kwargs.pop("ncol", self.legend.ncol),
            "columnspacing": kwargs.pop("columnspacing", self.legend.columnspacing),
            "labelspacing": kwargs.pop("labelspacing", self.legend.labelspacing),
            **kwargs,
        }

        legend = ax.legend(handles, labels, title=title, **legend_params)
        if title:
            legend.get_title().set_fontsize(self.legend.fontsize + 1)
            legend.get_title().set_fontweight("bold")
        return legend

    def get_status_color(self, status: str) -> str:
        """Get color for pattern status.

        Args:
            status: Pattern status (Stable, Draft, Stub, New)

        Returns:
            Color hex code
        """
        status_map = {
            "Stable": self.colors.stable,
            "Draft": self.colors.draft,
            "Stub": self.colors.stub,
            "New": self.colors.new,
        }
        return status_map.get(status, self.colors.stub)

    def get_importance_color(self, level: str) -> str:
        """Get color for importance level.

        Args:
            level: Importance level (high, medium, low)

        Returns:
            Color hex code
        """
        level_map = {
            "high": self.colors.high,
            "medium": self.colors.medium,
            "low": self.colors.low,
        }
        return level_map.get(level.lower(), self.colors.low)

    def get_color_sequence(self, n: int, palette: str = "primary") -> List[str]:
        """Get a sequence of colors from palette.

        Args:
            n: Number of colors needed
            palette: Palette name ("primary", "secondary", "accent")

        Returns:
            List of color hex codes
        """
        if palette == "primary":
            colors = self.colors.primary
        elif palette == "secondary":
            colors = self.colors.secondary
        elif palette == "accent":
            colors = self.colors.accent
        else:
            colors = self.colors.primary

        # Cycle if needed
        if n <= len(colors):
            return colors[:n]
        else:
            # Repeat palette
            return (colors * ((n // len(colors)) + 1))[:n]

    def format_axis_scientific(self, ax, axis: str = "y", precision: int = 2) -> None:
        """Format axis to use scientific notation.

        Args:
            ax: Matplotlib axes object
            axis: Axis to format ("x", "y", or "both")
            precision: Decimal precision
        """
        if not HAS_MATPLOTLIB:
            return

        from matplotlib.ticker import ScalarFormatter

        formatter = ScalarFormatter(useMathText=True)
        formatter.set_scientific(True)
        formatter.set_powerlimits((-2, 2))

        if axis in ("x", "both"):
            ax.xaxis.set_major_formatter(formatter)
        if axis in ("y", "both"):
            ax.yaxis.set_major_formatter(formatter)

    def format_axis_percentage(self, ax, axis: str = "y") -> None:
        """Format axis as percentage.

        Args:
            ax: Matplotlib axes object
            axis: Axis to format ("x", "y", or "both")
        """
        if not HAS_MATPLOTLIB:
            return

        from matplotlib.ticker import PercentFormatter

        if axis in ("x", "both"):
            ax.xaxis.set_major_formatter(PercentFormatter(1.0))
        if axis in ("y", "both"):
            ax.yaxis.set_major_formatter(PercentFormatter(1.0))

    def create_status_legend(self, ax, statuses: List[str]) -> None:
        """Create legend for pattern statuses.

        Args:
            ax: Matplotlib axes object
            statuses: List of status values to include
        """
        if not HAS_MATPLOTLIB:
            return

        handles = []
        labels = []
        for status in statuses:
            color = self.get_status_color(status)
            handles.append(Patch(facecolor=color, edgecolor="black", alpha=0.8))
            labels.append(status)

        self.create_legend(ax, handles, labels, title="Pattern Status")

    def create_importance_legend(self, ax, levels: List[str]) -> None:
        """Create legend for importance levels.

        Args:
            ax: Matplotlib axes object
            levels: List of importance levels to include
        """
        if not HAS_MATPLOTLIB:
            return

        handles = []
        labels = []
        for level in levels:
            color = self.get_importance_color(level)
            handles.append(Patch(facecolor=color, edgecolor="black", alpha=0.8))
            labels.append(level.capitalize())

        self.create_legend(ax, handles, labels, title="Importance Level")


# Global theme instance
_default_theme: Optional[VisualizationTheme] = None


def get_default_theme() -> VisualizationTheme:
    """Get the default visualization theme.

    Returns:
        Default VisualizationTheme instance
    """
    global _default_theme
    if _default_theme is None:
        _default_theme = VisualizationTheme()
    return _default_theme


def set_default_theme(theme: VisualizationTheme) -> None:
    """Set the default visualization theme.

    Args:
        theme: VisualizationTheme instance
    """
    global _default_theme
    _default_theme = theme


