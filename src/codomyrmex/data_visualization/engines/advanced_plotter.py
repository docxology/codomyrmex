"""Advanced data visualization: coordinator that composes plot mixins from submodules."""

import warnings

try:
    import matplotlib.pyplot as plt
    import numpy as np
    import seaborn as sns
except ImportError as _e:
    raise ImportError(
        "matplotlib, numpy, and seaborn are required for "
        "data_visualization.engines.advanced_plotter. "
        "Install with: uv sync --extra visualization"
    ) from _e

from codomyrmex.data_visualization._compat import monitor_performance
from codomyrmex.logging_monitoring import get_logger

# Import mixins for class composition
from ._dashboard import DashboardMixin, create_advanced_dashboard
from ._heatmap import HeatmapMixin, create_advanced_heatmap
from ._histogram import HistogramMixin, create_advanced_histogram
from ._line_bar import (
    LineBarMixin,
    create_advanced_bar_chart,
    create_advanced_line_plot,
)
from ._scatter import ScatterMixin, create_advanced_scatter_plot
from ._types import (
    ChartStyle,
    ColorPalette,
    DataPoint,
    Dataset,
    PlotConfig,
    PlotType,
    get_available_palettes,
    get_available_plot_types,
    get_available_styles,
    resolve_sns_palette,
    resolve_sns_style,
)

# Explicit __all__ so ruff knows these are intentional re-exports
__all__ = [
    "AdvancedPlotter",
    "ChartStyle",
    "ColorPalette",
    "DataPoint",
    "Dataset",
    "PlotConfig",
    "PlotType",
    "create_advanced_bar_chart",
    "create_advanced_dashboard",
    "create_advanced_heatmap",
    "create_advanced_histogram",
    "create_advanced_line_plot",
    "create_advanced_scatter_plot",
    "get_available_palettes",
    "get_available_plot_types",
    "get_available_styles",
]

logger = get_logger(__name__)

# Set up matplotlib and seaborn
plt.style.use("default")
sns.set_palette("husl")
warnings.filterwarnings("ignore", category=UserWarning)


class AdvancedPlotter(
    ScatterMixin,
    LineBarMixin,
    HeatmapMixin,
    HistogramMixin,
    DashboardMixin,
):
    """Advanced plotting class with comprehensive visualization capabilities."""

    def __init__(self, config: PlotConfig = None):  # type: ignore
        self.config = config or PlotConfig()
        self.figures = []
        self.current_figure = None
        self.current_axes = None

    def _setup_style(self):
        """Setup matplotlib and seaborn styling."""
        sns.set_style(resolve_sns_style(self.config.style))

    def _get_color_palette(self, n_colors: int) -> list[str]:
        """Get color palette for plotting."""
        return sns.color_palette(resolve_sns_palette(self.config.palette), n_colors)

    @monitor_performance("create_figure")
    def create_figure(
        self, subplots: tuple[int, int] = (1, 1), **kwargs
    ) -> tuple[plt.Figure, plt.Axes | np.ndarray]:
        """Create a new figure and axes."""
        self._setup_style()
        figsize = kwargs.get("figsize", self.config.figsize)
        dpi = kwargs.get("dpi", self.config.dpi)

        fig, axes = plt.subplots(
            subplots[0],
            subplots[1],
            figsize=figsize,
            dpi=dpi,
            **{k: v for k, v in kwargs.items() if k not in ["figsize", "dpi"]},
        )

        self.current_figure = fig
        self.current_axes = axes
        self.figures.append(fig)
        return fig, axes

    @monitor_performance("finalize_plot")
    def finalize_plot(
        self,
        title: str | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        legend: bool | None = None,
        grid: bool | None = None,
        save_path: str | None = None,
    ) -> plt.Figure:
        """Finalize the current plot with labels, legend, and styling."""
        if self.current_figure is None:
            raise ValueError("No current figure to finalize")

        self._set_plot_title(title)
        self._set_plot_labels(xlabel, ylabel)
        self._set_plot_legend(legend)
        self._set_plot_grid(grid)

        if self.config.tight_layout:
            self.current_figure.tight_layout()

        if save_path:
            self.save_plot(save_path)

        if self.config.show_plot:
            plt.show()

        return self.current_figure

    def _iter_axes(self):
        """Yield individual axes from current_axes (single or multi-subplot)."""
        axes = self.current_axes
        if hasattr(axes, "flat"):
            yield from axes.flat  # type: ignore
        elif hasattr(axes, "__iter__"):
            yield from axes  # type: ignore
        else:
            yield axes

    def _set_plot_title(self, title: str | None = None) -> None:
        if title or self.config.title:
            self.current_figure.suptitle(title or self.config.title)

    def _set_plot_labels(
        self, xlabel: str | None = None, ylabel: str | None = None
    ) -> None:
        for ax in self._iter_axes():
            if hasattr(ax, "set_xlabel"):
                ax.set_xlabel(xlabel or self.config.xlabel)
                ax.set_ylabel(ylabel or self.config.ylabel)

    def _set_plot_legend(self, legend: bool | None = None) -> None:
        if not (legend if legend is not None else self.config.legend):
            return
        for ax in self._iter_axes():
            if hasattr(ax, "legend"):
                ax.legend()

    def _set_plot_grid(self, grid: bool | None = None) -> None:
        if not (grid if grid is not None else self.config.grid):
            return
        for ax in self._iter_axes():
            if hasattr(ax, "grid"):
                ax.grid(True, alpha=0.3)

    @monitor_performance("save_plot")
    def save_plot(
        self,
        path: str,
        format: str | None = None,
        dpi: int | None = None,
        bbox_inches: str | None = None,
        transparent: bool | None = None,
    ) -> bool:
        """Save the current plot to a file."""
        if self.current_figure is None:
            logger.error("No current figure to save")
            return False

        format = format or self.config.save_format
        dpi = dpi or self.config.save_dpi
        bbox_inches = bbox_inches or self.config.bbox_inches
        transparent = (
            transparent if transparent is not None else self.config.transparent
        )

        try:
            self.current_figure.savefig(
                path,
                format=format,
                dpi=dpi,
                bbox_inches=bbox_inches,
                transparent=transparent,
            )
        except OSError as e:
            logger.error(f"Failed to save plot to {path}: {e}")
            return False

        logger.info(f"Plot saved to {path}")
        return True

    def _plot_dataset(self, ax: plt.Axes, dataset: "Dataset") -> None:
        """Render a single Dataset onto *ax* based on its plot_type.

        Dispatches to the appropriate matplotlib call for LINE, SCATTER, BAR,
        and HISTOGRAM plot types.  Adds a legend entry when dataset.label is set.
        """
        xs = [p.x for p in dataset.data]
        ys = [p.y for p in dataset.data]
        label = dataset.label
        color = dataset.color

        if dataset.plot_type == PlotType.LINE:
            ax.plot(xs, ys, label=label, color=color, linewidth=dataset.linewidth)
        elif dataset.plot_type == PlotType.SCATTER:
            sizes = [
                p.size if p.size is not None else dataset.markersize
                for p in dataset.data
            ]
            colors = [
                p.color if p.color is not None else (color or "blue")
                for p in dataset.data
            ]
            ax.scatter(xs, ys, s=sizes, c=colors, label=label, alpha=dataset.alpha)
        elif dataset.plot_type == PlotType.BAR:
            ax.bar(xs, ys, label=label, color=color)
        elif dataset.plot_type == PlotType.HISTOGRAM:
            ax.hist(ys, label=label)

        if label:
            ax.legend()

    def clear_figures(self):
        """Clear all figures from memory."""
        for fig in self.figures:
            plt.close(fig)
        self.figures.clear()
        self.current_figure = None
        self.current_axes = None
