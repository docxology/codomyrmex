"""Advanced data visualization functionality for Codomyrmex.

This module provides comprehensive plotting capabilities including statistical plots,
interactive visualizations, dashboard generation, and data analysis charts.
"""

import warnings
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
except ImportError:
    from logging import getLogger as get_logger

try:
    from codomyrmex.performance import monitor_performance, performance_context
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        """No-op decorator."""
        def decorator(func):
            return func
        return decorator

    class performance_context:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass





# Get module logger
logger = get_logger(__name__)

# Set up matplotlib and seaborn
plt.style.use("default")
sns.set_palette("husl")
warnings.filterwarnings("ignore", category=UserWarning)

# Enums for plot types and styles
class PlotType(Enum):
    """Types of plots available."""

    LINE = "line"
    SCATTER = "scatter"
    BAR = "bar"
    HISTOGRAM = "histogram"
    PIE = "pie"
    HEATMAP = "heatmap"
    BOX = "box"
    VIOLIN = "violin"
    DENSITY = "density"
    CORRELATION = "correlation"
    TIMESERIES = "timeseries"
    DASHBOARD = "dashboard"
    INTERACTIVE = "interactive"

class ChartStyle(Enum):
    """Chart styling options."""

    DEFAULT = "default"
    MINIMAL = "minimal"
    DARK = "dark"
    WHITE = "white"
    TICKS = "ticks"
    DARKGRID = "darkgrid"
    WHITEGRID = "whitegrid"

class ColorPalette(Enum):
    """Color palette options."""

    DEFAULT = "default"
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    COOLWARM = "coolwarm"
    RAINBOW = "rainbow"
    PASTEL = "pastel"
    DARK = "dark"
    BRIGHT = "bright"

@dataclass
class PlotConfig:
    """Configuration for plot generation."""

    title: str = ""
    xlabel: str = ""
    ylabel: str = ""
    figsize: tuple[int, int] = (10, 6)
    dpi: int = 100
    style: ChartStyle = ChartStyle.DEFAULT
    palette: ColorPalette = ColorPalette.DEFAULT
    grid: bool = True
    legend: bool = True
    tight_layout: bool = True
    save_format: str = "png"
    save_dpi: int = 300
    show_plot: bool = True
    transparent: bool = False
    bbox_inches: str = "tight"

@dataclass
class DataPoint:
    """Individual data point for plotting."""

    x: float | int | str | datetime
    y: float | int | str | datetime
    label: str | None = None
    color: str | None = None
    size: float | None = None
    alpha: float = 1.0

@dataclass
class Dataset:
    """Dataset for plotting."""

    name: str
    data: list[DataPoint]
    plot_type: PlotType
    color: str | None = None
    label: str | None = None
    alpha: float = 1.0
    linewidth: float = 2.0
    markersize: float = 6.0

class AdvancedPlotter:
    """Advanced plotting class with comprehensive visualization capabilities."""

    def __init__(self, config: PlotConfig = None):
        """
        Initialize the advanced plotter.

        Args:
            config: Plot configuration settings
        """
        self.config = config or PlotConfig()
        self.figures = []
        self.current_figure = None
        self.current_axes = None

    def _setup_style(self):
        """Setup matplotlib and seaborn styling."""
        if self.config.style == ChartStyle.MINIMAL:
            sns.set_style("white")
        elif self.config.style == ChartStyle.DARK:
            sns.set_style("dark")
        elif self.config.style == ChartStyle.WHITE:
            sns.set_style("white")
        elif self.config.style == ChartStyle.TICKS:
            sns.set_style("ticks")
        elif self.config.style == ChartStyle.DARKGRID:
            sns.set_style("darkgrid")
        elif self.config.style == ChartStyle.WHITEGRID:
            sns.set_style("whitegrid")
        else:
            sns.set_style("whitegrid")

    def _get_color_palette(self, n_colors: int) -> list[str]:
        """Get color palette for plotting."""
        if self.config.palette == ColorPalette.VIRIDIS:
            return sns.color_palette("viridis", n_colors)
        elif self.config.palette == ColorPalette.PLASMA:
            return sns.color_palette("plasma", n_colors)
        elif self.config.palette == ColorPalette.INFERNO:
            return sns.color_palette("inferno", n_colors)
        elif self.config.palette == ColorPalette.MAGMA:
            return sns.color_palette("magma", n_colors)
        elif self.config.palette == ColorPalette.COOLWARM:
            return sns.color_palette("coolwarm", n_colors)
        elif self.config.palette == ColorPalette.RAINBOW:
            return sns.color_palette("rainbow", n_colors)
        elif self.config.palette == ColorPalette.PASTEL:
            return sns.color_palette("pastel", n_colors)
        elif self.config.palette == ColorPalette.DARK:
            return sns.color_palette("dark", n_colors)
        elif self.config.palette == ColorPalette.BRIGHT:
            return sns.color_palette("bright", n_colors)
        else:
            return sns.color_palette("husl", n_colors)

    @monitor_performance("create_figure")
    def create_figure(
        self, subplots: tuple[int, int] = (1, 1), **kwargs
    ) -> tuple[plt.Figure, plt.Axes | np.ndarray]:
        """
        Create a new figure and axes.

        Args:
            subplots: Number of subplots (rows, cols)
            **kwargs: Additional arguments for plt.subplots

        Returns:
            Tuple of (figure, axes)
        """
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

    @monitor_performance("plot_line")
    def plot_line(
        self,
        x_data: list[float | int | str | datetime],
        y_data: list[float | int | str | datetime],
        label: str = "",
        color: str = None,
        linewidth: float = 2.0,
        linestyle: str = "-",
        marker: str = None,
        markersize: float = 6.0,
        alpha: float = 1.0,
        **kwargs,
    ) -> plt.Line2D:
        """
        Create a line plot.

        Args:
            x_data: X-axis data
            y_data: Y-axis data
            label: Line label for legend
            color: Line color
            linewidth: Line width
            linestyle: Line style
            marker: Marker style
            markersize: Marker size
            alpha: Transparency
            **kwargs: Additional arguments for plt.plot

        Returns:
            Line2D object
        """
        if self.current_axes is None:
            self.create_figure()

        axes = (
            self.current_axes
            if hasattr(self.current_axes, "plot")
            else self.current_axes[0]
        )

        line = axes.plot(
            x_data,
            y_data,
            label=label,
            color=color,
            linewidth=linewidth,
            linestyle=linestyle,
            marker=marker,
            markersize=markersize,
            alpha=alpha,
            **kwargs,
        )[0]

        return line

    @monitor_performance("plot_scatter")
    def plot_scatter(
        self,
        x_data: list[float | int | str | datetime],
        y_data: list[float | int | str | datetime],
        label: str = "",
        color: str = None,
        size: float | list[float] = 50,
        alpha: float = 0.7,
        marker: str = "o",
        **kwargs,
    ):
        """
        Create a scatter plot.

        Args:
            x_data: X-axis data
            y_data: Y-axis data
            label: Scatter label for legend
            color: Point color
            size: Point size
            alpha: Transparency
            marker: Marker style
            **kwargs: Additional arguments for plt.scatter

        Returns:
            PathCollection object
        """
        if self.current_axes is None:
            self.create_figure()

        axes = (
            self.current_axes
            if hasattr(self.current_axes, "scatter")
            else self.current_axes[0]
        )

        scatter = axes.scatter(
            x_data,
            y_data,
            label=label,
            c=color,
            s=size,
            alpha=alpha,
            marker=marker,
            **kwargs,
        )

        return scatter

    @monitor_performance("plot_bar")
    def plot_bar(
        self,
        x_data: list[str | int | float],
        y_data: list[float | int],
        label: str = "",
        color: str | list[str] = None,
        alpha: float = 0.8,
        width: float = 0.8,
        orientation: str = "vertical",
        **kwargs,
    ):
        """
        Create a bar chart.

        Args:
            x_data: X-axis categories
            y_data: Y-axis values
            label: Bar label for legend
            color: Bar color(s)
            alpha: Transparency
            width: Bar width
            orientation: Bar orientation ("vertical" or "horizontal")
            **kwargs: Additional arguments for plt.bar

        Returns:
            BarContainer object
        """
        if self.current_axes is None:
            self.create_figure()

        axes = (
            self.current_axes
            if hasattr(self.current_axes, "bar")
            else self.current_axes[0]
        )

        if orientation == "horizontal":
            bars = axes.barh(
                x_data,
                y_data,
                label=label,
                color=color,
                alpha=alpha,
                height=width,
                **kwargs,
            )
        else:
            bars = axes.bar(
                x_data,
                y_data,
                label=label,
                color=color,
                alpha=alpha,
                width=width,
                **kwargs,
            )

        return bars

    @monitor_performance("plot_histogram")
    def plot_histogram(
        self,
        data: list[float | int],
        bins: int | list[float] = 30,
        label: str = "",
        color: str = None,
        alpha: float = 0.7,
        density: bool = False,
        cumulative: bool = False,
        **kwargs,
    ):
        """
        Create a histogram.

        Args:
            data: Data to histogram
            bins: Number of bins or bin edges
            label: Histogram label for legend
            color: Bar color
            alpha: Transparency
            density: Whether to normalize to density
            cumulative: Whether to show cumulative distribution
            **kwargs: Additional arguments for plt.hist

        Returns:
            Tuple of (counts, bin_edges, patches)
        """
        if self.current_axes is None:
            self.create_figure()

        axes = (
            self.current_axes
            if hasattr(self.current_axes, "hist")
            else self.current_axes[0]
        )

        counts, bin_edges, patches = axes.hist(
            data,
            bins=bins,
            label=label,
            color=color,
            alpha=alpha,
            density=density,
            cumulative=cumulative,
            **kwargs,
        )

        return counts, bin_edges, patches

    @monitor_performance("plot_heatmap")
    def plot_heatmap(
        self,
        data: list[list[float]] | np.ndarray | pd.DataFrame,
        x_labels: list[str] = None,
        y_labels: list[str] = None,
        cmap: str = "viridis",
        annot: bool = False,
        fmt: str = ".2f",
        cbar: bool = True,
        **kwargs,
    ):
        """
        Create a heatmap.

        Args:
            data: 2D data for heatmap
            x_labels: X-axis labels
            y_labels: Y-axis labels
            cmap: Colormap
            annot: Whether to annotate cells
            fmt: Annotation format
            cbar: Whether to show colorbar
            **kwargs: Additional arguments for sns.heatmap

        Returns:
            AxesImage object
        """
        if self.current_axes is None:
            self.create_figure()

        axes = (
            self.current_axes
            if hasattr(self.current_axes, "imshow")
            else self.current_axes[0]
        )

        if isinstance(data, list):
            data = np.array(data)

        heatmap = sns.heatmap(
            data,
            xticklabels=x_labels,
            yticklabels=y_labels,
            cmap=cmap,
            annot=annot,
            fmt=fmt,
            cbar=cbar,
            ax=axes,
            **kwargs,
        )

        return heatmap

    @monitor_performance("plot_box")
    def plot_box(
        self,
        data: list[float | int] | dict[str, list[float | int]],
        labels: list[str] = None,
        color: str | list[str] = None,
        notch: bool = False,
        patch_artist: bool = True,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Create a box plot.

        Args:
            data: Data for box plot (list or dict of lists)
            labels: Box labels
            color: Box color(s)
            notch: Whether to show notches
            patch_artist: Whether to fill boxes
            **kwargs: Additional arguments for plt.boxplot

        Returns:
            Dictionary of box plot elements
        """
        if self.current_axes is None:
            self.create_figure()

        axes = (
            self.current_axes
            if hasattr(self.current_axes, "boxplot")
            else self.current_axes[0]
        )

        if isinstance(data, dict):
            data_list = list(data.values())
            labels = labels or list(data.keys())
        else:
            data_list = [data]
            labels = labels or [""]

        box_plot = axes.boxplot(
            data_list, labels=labels, notch=notch, patch_artist=patch_artist, **kwargs
        )

        if color and patch_artist:
            if isinstance(color, str):
                color = [color] * len(data_list)
            for patch, col in zip(box_plot["boxes"], color):
                patch.set_facecolor(col)

        return box_plot

    @monitor_performance("plot_violin")
    def plot_violin(
        self,
        data: list[float | int] | dict[str, list[float | int]],
        labels: list[str] = None,
        color: str | list[str] = None,
        alpha: float = 0.7,
        **kwargs,
    ) -> list[plt.Polygon]:
        """
        Create a violin plot.

        Args:
            data: Data for violin plot (list or dict of lists)
            labels: Violin labels
            color: Violin color(s)
            alpha: Transparency
            **kwargs: Additional arguments for sns.violinplot

        Returns:
            List of violin plot elements
        """
        if self.current_axes is None:
            self.create_figure()

        axes = (
            self.current_axes
            if hasattr(self.current_axes, "violinplot")
            else self.current_axes[0]
        )

        if isinstance(data, dict):
            # Convert dict to long format for seaborn
            df_data = []
            for label, values in data.items():
                for value in values:
                    df_data.append({"label": label, "value": value})
            df = pd.DataFrame(df_data)

            violin_plot = sns.violinplot(
                data=df,
                x="label",
                y="value",
                color=color,
                alpha=alpha,
                ax=axes,
                **kwargs,
            )
        else:
            # Single dataset
            df = pd.DataFrame({"value": data, "label": labels[0] if labels else "data"})

            violin_plot = sns.violinplot(
                data=df,
                x="label",
                y="value",
                color=color,
                alpha=alpha,
                ax=axes,
                **kwargs,
            )

        return violin_plot

    @monitor_performance("plot_correlation")
    def plot_correlation(
        self,
        data: pd.DataFrame | np.ndarray,
        method: str = "pearson",
        cmap: str = "coolwarm",
        annot: bool = True,
        fmt: str = ".2f",
        **kwargs,
    ):
        """
        Create a correlation heatmap.

        Args:
            data: Data for correlation analysis
            method: Correlation method ("pearson", "spearman", "kendall")
            cmap: Colormap
            annot: Whether to annotate cells
            fmt: Annotation format
            **kwargs: Additional arguments for sns.heatmap

        Returns:
            AxesImage object
        """
        if self.current_axes is None:
            self.create_figure()

        axes = (
            self.current_axes
            if hasattr(self.current_axes, "imshow")
            else self.current_axes[0]
        )

        if isinstance(data, list):
            data = np.array(data)

        if isinstance(data, np.ndarray) and data.ndim == 2:
            data = pd.DataFrame(data)

        corr_matrix = data.corr(method=method)

        heatmap = sns.heatmap(
            corr_matrix,
            cmap=cmap,
            annot=annot,
            fmt=fmt,
            center=0,
            square=True,
            ax=axes,
            **kwargs,
        )

        return heatmap

    @monitor_performance("create_dashboard")
    def create_dashboard(
        self,
        datasets: list[Dataset],
        layout: tuple[int, int] = (2, 2),
        title: str = "Dashboard",
        **kwargs,
    ) -> plt.Figure:
        """
        Create a multi-panel dashboard.

        Args:
            datasets: List of datasets to plot
            layout: Dashboard layout (rows, cols)
            title: Dashboard title
            **kwargs: Additional arguments for subplots

        Returns:
            Figure object
        """
        fig, axes = self.create_figure(subplots=layout, **kwargs)

        if not hasattr(axes, "__iter__"):
            axes = [axes]
        elif axes.ndim == 1:
            axes = axes.flatten()
        else:
            axes = axes.flatten()

        for i, dataset in enumerate(datasets):
            if i >= len(axes):
                break

            ax = axes[i]
            self._plot_dataset(ax, dataset)

        # Hide unused subplots
        for i in range(len(datasets), len(axes)):
            axes[i].set_visible(False)

        fig.suptitle(title, fontsize=16, fontweight="bold")

        if self.config.tight_layout:
            fig.tight_layout()

        return fig

    def _plot_dataset(self, ax: plt.Axes, dataset: Dataset):
        """Plot a single dataset on given axes."""
        x_data = [point.x for point in dataset.data]
        y_data = [point.y for point in dataset.data]

        if dataset.plot_type == PlotType.LINE:
            ax.plot(
                x_data,
                y_data,
                color=dataset.color,
                label=dataset.label,
                alpha=dataset.alpha,
                linewidth=dataset.linewidth,
                markersize=dataset.markersize,
            )
        elif dataset.plot_type == PlotType.SCATTER:
            sizes = [point.size or dataset.markersize for point in dataset.data]
            colors = [point.color or dataset.color for point in dataset.data]
            ax.scatter(
                x_data,
                y_data,
                c=colors,
                s=sizes,
                label=dataset.label,
                alpha=dataset.alpha,
            )
        elif dataset.plot_type == PlotType.BAR:
            ax.bar(
                x_data,
                y_data,
                color=dataset.color,
                label=dataset.label,
                alpha=dataset.alpha,
            )
        elif dataset.plot_type == PlotType.HISTOGRAM:
            ax.hist(
                y_data, color=dataset.color, label=dataset.label, alpha=dataset.alpha
            )

        if dataset.label:
            ax.legend()

    @monitor_performance("finalize_plot")
    def finalize_plot(
        self,
        title: str = None,
        xlabel: str = None,
        ylabel: str = None,
        legend: bool = None,
        grid: bool = None,
        save_path: str = None,
    ) -> plt.Figure:
        """
        Finalize the current plot with labels, legend, and styling.

        Args:
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            legend: Whether to show legend
            grid: Whether to show grid
            save_path: Path to save the plot

        Returns:
            Figure object
        """
        if self.current_figure is None:
            raise ValueError("No current figure to finalize")

        # Set title
        self._set_plot_title(title)

        # Set labels
        self._set_plot_labels(xlabel, ylabel)

        # Set legend
        self._set_plot_legend(legend)

        # Set grid
        self._set_plot_grid(grid)

        # Apply tight layout
        if self.config.tight_layout:
            self.current_figure.tight_layout()

        # Save plot
        if save_path:
            self.save_plot(save_path)

        # Show plot
        if self.config.show_plot:
            plt.show()

        return self.current_figure

    def _set_plot_title(self, title: str = None) -> None:
        """Set the plot title."""
        if title or self.config.title:
            self.current_figure.suptitle(title or self.config.title)

    def _set_plot_labels(self, xlabel: str = None, ylabel: str = None) -> None:
        """Set axis labels for single or multiple axes."""
        axes = self.current_axes

        if hasattr(axes, "set_xlabel"):
            # Single axis
            axes.set_xlabel(xlabel or self.config.xlabel)
            axes.set_ylabel(ylabel or self.config.ylabel)
        elif hasattr(axes, "__iter__"):
            # Multiple axes (subplots)
            for ax in axes.flat:
                if hasattr(ax, "set_xlabel"):
                    ax.set_xlabel(xlabel or self.config.xlabel)
                    ax.set_ylabel(ylabel or self.config.ylabel)

    def _set_plot_legend(self, legend: bool = None) -> None:
        """Set legend for single or multiple axes."""
        if legend is None:
            legend = self.config.legend

        if not legend:
            return

        axes = self.current_axes

        if hasattr(axes, "legend"):
            # Single axis
            axes.legend()
        elif hasattr(axes, "__iter__"):
            # Multiple axes (subplots)
            for ax in axes.flat:
                if hasattr(ax, "legend"):
                    ax.legend()

    def _set_plot_grid(self, grid: bool = None) -> None:
        """Set grid for single or multiple axes."""
        if grid is None:
            grid = self.config.grid

        if not grid:
            return

        axes = self.current_axes

        if hasattr(axes, "grid"):
            # Single axis
            axes.grid(True, alpha=0.3)
        elif hasattr(axes, "__iter__"):
            # Multiple axes (subplots)
            for ax in axes.flat:
                if hasattr(ax, "grid"):
                    ax.grid(True, alpha=0.3)

    @monitor_performance("save_plot")
    def save_plot(
        self,
        path: str,
        format: str = None,
        dpi: int = None,
        bbox_inches: str = None,
        transparent: bool = None,
    ) -> bool:
        """
        Save the current plot to a file.

        Args:
            path: File path to save to
            format: File format (png, pdf, svg, etc.)
            dpi: Resolution
            bbox_inches: Bounding box
            transparent: Whether to make background transparent

        Returns:
            True if successful, False otherwise
        """
        if self.current_figure is None:
            logger.error("No current figure to save")
            return False

        try:
            format = format or self.config.save_format
            dpi = dpi or self.config.save_dpi
            bbox_inches = bbox_inches or self.config.bbox_inches
            transparent = (
                transparent if transparent is not None else self.config.transparent
            )

            self.current_figure.savefig(
                path,
                format=format,
                dpi=dpi,
                bbox_inches=bbox_inches,
                transparent=transparent,
            )

            logger.info(f"Plot saved to {path}")
            return True

        except Exception as e:
            logger.error(f"Error saving plot: {e}")
            return False

    def clear_figures(self):
        """Clear all figures from memory."""
        for fig in self.figures:
            plt.close(fig)
        self.figures.clear()
        self.current_figure = None
        self.current_axes = None

# Convenience functions
def create_advanced_line_plot(
    x_data: list[float | int | str | datetime],
    y_data: list[float | int | str | datetime],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    config: PlotConfig = None,
    save_path: str = None,
    **kwargs,
) -> plt.Figure:
    """Create an advanced line plot."""
    plotter = AdvancedPlotter(config)
    plotter.plot_line(x_data, y_data, **kwargs)
    return plotter.finalize_plot(title, xlabel, ylabel, save_path=save_path)

def create_advanced_scatter_plot(
    x_data: list[float | int | str | datetime],
    y_data: list[float | int | str | datetime],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    config: PlotConfig = None,
    **kwargs,
) -> plt.Figure:
    """Create an advanced scatter plot."""
    plotter = AdvancedPlotter(config)
    plotter.plot_scatter(x_data, y_data, **kwargs)
    return plotter.finalize_plot(title, xlabel, ylabel)

def create_advanced_bar_chart(
    x_data: list[str | int | float],
    y_data: list[float | int],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    config: PlotConfig = None,
    save_path: str = None,
    **kwargs,
) -> plt.Figure:
    """Create an advanced bar chart."""
    plotter = AdvancedPlotter(config)
    plotter.plot_bar(x_data, y_data, **kwargs)
    return plotter.finalize_plot(title, xlabel, ylabel, save_path=save_path)

def create_advanced_histogram(
    data: list[float | int],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    config: PlotConfig = None,
    **kwargs,
) -> plt.Figure:
    """Create an advanced histogram."""
    plotter = AdvancedPlotter(config)
    plotter.plot_histogram(data, **kwargs)
    return plotter.finalize_plot(title, xlabel, ylabel)

def create_advanced_heatmap(
    data: list[list[float]] | np.ndarray | pd.DataFrame,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    config: PlotConfig = None,
    **kwargs,
) -> plt.Figure:
    """Create an advanced heatmap."""
    plotter = AdvancedPlotter(config)
    plotter.plot_heatmap(data, **kwargs)
    return plotter.finalize_plot(title, xlabel, ylabel)

def create_advanced_dashboard(
    datasets: list[Dataset],
    title: str = "Dashboard",
    layout: tuple[int, int] = (2, 2),
    config: PlotConfig = None,
    **kwargs,
) -> plt.Figure:
    """Create an advanced dashboard."""
    plotter = AdvancedPlotter(config)
    return plotter.create_dashboard(datasets, layout, title, **kwargs)

def get_available_styles() -> list[ChartStyle]:
    """Get list of available chart styles."""
    return list(ChartStyle)

def get_available_palettes() -> list[ColorPalette]:
    """Get list of available color palettes."""
    return list(ColorPalette)

def get_available_plot_types() -> list[PlotType]:
    """Get list of available plot types."""
    return list(PlotType)
