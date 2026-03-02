from abc import ABC
from typing import TYPE_CHECKING, Any

import matplotlib
import matplotlib.colors
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from codomyrmex.cerebrum.core.exceptions import VisualizationError
from codomyrmex.cerebrum.visualization.theme import (
    VisualizationTheme,
    get_default_theme,
)
from codomyrmex.logging_monitoring import get_logger

try:
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    Figure = Any
    Axes = Any
    plt = None

try:
    import networkx as nx
except ImportError:
    nx = None

if TYPE_CHECKING:
    pass
else:
    if nx is None:
        # Create a dummy type for nx when not available
        class _DummyGraph:
            """Functional component: _DummyGraph."""
            pass
        class _DummyNX:
            """Functional component: _DummyNX."""
            Graph = _DummyGraph
            DiGraph = _DummyGraph
        nx = _DummyNX()

logger = get_logger(__name__)


class BaseVisualizer(ABC):
    """Base class for all visualizers."""

    def __init__(
        self,
        figure_size: tuple[float, float] = (12.0, 8.0),
        dpi: int = 300,
        theme: VisualizationTheme | None = None,
    ):
        """Initialize base visualizer.

        Args:
            figure_size: Figure size (width, height) in inches
            dpi: DPI for figures
            theme: Visualization theme (default: use global theme)
        """
        if not HAS_MATPLOTLIB:
            raise VisualizationError("matplotlib is required for visualization")

        self.figure_size = figure_size
        self.dpi = dpi
        self.theme = theme or get_default_theme()
        self.logger = get_logger(__name__)

    def create_figure(self, nrows: int = 1, ncols: int = 1, **kwargs) -> tuple[Figure, Any]:
        """Create a figure with theme applied.

        Args:
            nrows: Number of rows
            ncols: Number of columns
            **kwargs: Additional subplot parameters

        Returns:
            Tuple of (figure, axes)
        """
        figsize = kwargs.pop("figsize", self.figure_size)
        dpi = kwargs.pop("dpi", self.dpi)

        fig, axes = plt.subplots(
            nrows=nrows, ncols=ncols, figsize=figsize, dpi=dpi, **kwargs
        )

        # Apply theme to all axes
        if nrows == 1 and ncols == 1:
            self.theme.apply_to_axes(axes)
        else:
            for ax in axes.flatten() if hasattr(axes, "flatten") else [axes]:
                self.theme.apply_to_axes(ax)

        return fig, axes

    def format_title(self, ax: Axes, title: str, **kwargs) -> None:
        """Format and set title.

        Args:
            ax: Matplotlib axes
            title: Title text
            **kwargs: Additional title parameters
        """
        fontsize = kwargs.pop("fontsize", self.theme.font.title_size)
        fontweight = kwargs.pop("fontweight", self.theme.font.weight_title)
        pad = kwargs.pop("pad", self.theme.axis.title_pad)

        ax.set_title(title, fontsize=fontsize, fontweight=fontweight, pad=pad, **kwargs)

    def format_axes_labels(
        self, ax: Axes, xlabel: str | None = None, ylabel: str | None = None, **kwargs
    ) -> None:
        """Format and set axis labels.

        Args:
            ax: Matplotlib axes
            xlabel: X-axis label
            ylabel: Y-axis label
            **kwargs: Additional label parameters
        """
        fontsize = kwargs.pop("fontsize", self.theme.font.label_size)
        fontweight = kwargs.pop("fontweight", self.theme.font.weight_label)
        labelpad = kwargs.pop("labelpad", self.theme.axis.label_pad)

        if xlabel:
            ax.set_xlabel(xlabel, fontsize=fontsize, fontweight=fontweight, labelpad=labelpad, **kwargs)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=fontsize, fontweight=fontweight, labelpad=labelpad, **kwargs)

    def save_figure(
        self, fig: Figure, output_path: str, **kwargs
    ) -> None:
        """Save figure with theme defaults.

        Args:
            fig: Matplotlib figure
            output_path: Output file path
            **kwargs: Additional save parameters
        """
        bbox_inches = kwargs.pop("bbox_inches", self.theme.figure.save_bbox_inches)
        dpi = kwargs.pop("dpi", self.dpi)
        format = kwargs.pop("format", self.theme.figure.save_format)

        fig.savefig(
            output_path, dpi=dpi, bbox_inches=bbox_inches, format=format, **kwargs
        )
        plt.close(fig)
        self.logger.debug(f"Saved figure to {output_path}")


class BaseNetworkVisualizer(BaseVisualizer):
    """Base class for network visualizations."""

    def __init__(
        self,
        figure_size: tuple[float, float] = (12.0, 8.0),
        dpi: int = 300,
        theme: VisualizationTheme | None = None,
    ):
        """Initialize network visualizer.

        Args:
            figure_size: Figure size
            dpi: DPI
            theme: Visualization theme
        """
        super().__init__(figure_size, dpi, theme)

    def get_node_colors(
        self,
        G: nx.Graph,
        attribute: str,
        color_map: dict[str, str] | None = None,
    ) -> list[str]:
        """Get node colors based on attribute.

        Args:
            G: NetworkX graph
            attribute: Node attribute name
            color_map: Optional custom color mapping

        Returns:
            List of colors for each node
        """
        if color_map is None:
            # Use theme colors
            if attribute == "status":
                color_map = {
                    status: self.theme.get_status_color(status)
                    for status in ["Stable", "Draft", "Stub", "New"]
                }
            else:
                # Use primary palette
                unique_vals = sorted({G.nodes[node].get(attribute, "default") for node in G.nodes()})
                colors = self.theme.get_color_sequence(len(unique_vals), "primary")
                color_map = {val: colors[i] for i, val in enumerate(unique_vals)}

        colors = []
        for node in G.nodes():
            attr_value = G.nodes[node].get(attribute, "default")
            colors.append(color_map.get(attr_value, self.theme.colors.node_default))

        return colors

    def get_node_sizes(
        self,
        G: nx.Graph,
        metric: str = "degree",
        min_size: float = 100.0,
        max_size: float = 2000.0,
    ) -> list[float]:
        """Get node sizes based on importance metric.

        Args:
            G: NetworkX graph
            metric: Importance metric ("degree", "betweenness", "pagerank", "eigenvector")
            min_size: Minimum node size
            max_size: Maximum node size

        Returns:
            List of sizes for each node
        """
        if metric == "degree":
            importances = dict(G.degree())
        elif metric == "betweenness":
            importances = nx.betweenness_centrality(G)
        elif metric == "pagerank":
            importances = nx.pagerank(G)
        elif metric == "eigenvector":
            importances = nx.eigenvector_centrality(G, max_iter=100)
        else:
            importances = dict(G.degree())

        if not importances:
            return [min_size] * len(G.nodes())

        values = list(importances.values())
        min_val = min(values)
        max_val = max(values)

        if max_val == min_val:
            return [min_size] * len(G.nodes())

        # Scale to size range
        sizes = [
            min_size + (importances.get(node, 0) - min_val) / (max_val - min_val) * (max_size - min_size)
            for node in G.nodes()
        ]

        return sizes

    def get_edge_widths(
        self,
        G: nx.Graph,
        weight_attr: str = "weight",
        min_width: float = 0.5,
        max_width: float = 3.0,
    ) -> list[float]:
        """Get edge widths based on weight attribute.

        Args:
            G: NetworkX graph
            weight_attr: Edge weight attribute name
            min_width: Minimum edge width
            max_width: Maximum edge width

        Returns:
            List of widths for each edge
        """
        weights = []
        for u, v in G.edges():
            weight = G[u][v].get(weight_attr, 1.0)
            weights.append(weight)

        if not weights:
            return []

        min_weight = min(weights)
        max_weight = max(weights)

        if max_weight == min_weight:
            return [min_width] * len(weights)

        # Scale to width range
        widths = [
            min_width + (w - min_weight) / (max_weight - min_weight) * (max_width - min_width)
            for w in weights
        ]

        return widths

    def apply_layout(
        self,
        G: nx.Graph,
        layout: str = "spring",
        **kwargs,
    ) -> dict[str, tuple[float, float]]:
        """Apply layout algorithm to graph.

        Args:
            G: NetworkX graph
            layout: Layout type ("spring", "circular", "hierarchical", "kamada_kawai")
            **kwargs: Layout-specific parameters

        Returns:
            Dictionary mapping node IDs to (x, y) positions
        """
        if layout == "spring":
            k = kwargs.pop("k", 1.0 / np.sqrt(len(G.nodes())) if len(G.nodes()) > 0 else 1.0)
            iterations = kwargs.pop("iterations", 50)
            pos = nx.spring_layout(G, k=k, iterations=iterations, **kwargs)
        elif layout == "circular":
            pos = nx.circular_layout(G, **kwargs)
        elif layout == "hierarchical":
            try:
                pos = nx.nx_agraph.graphviz_layout(G, prog="dot", **kwargs)
            except Exception:
                # Fallback to spring layout
                pos = nx.spring_layout(G, k=2, iterations=100, **kwargs)
        elif layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(G, **kwargs)
        else:
            pos = nx.spring_layout(G, **kwargs)

        return pos


class BaseChartVisualizer(BaseVisualizer):
    """Base class for chart visualizations (bars, lines, distributions)."""

    def __init__(
        self,
        figure_size: tuple[float, float] = (12.0, 8.0),
        dpi: int = 300,
        theme: VisualizationTheme | None = None,
    ):
        """Initialize chart visualizer.

        Args:
            figure_size: Figure size
            dpi: DPI
            theme: Visualization theme
        """
        super().__init__(figure_size, dpi, theme)

    def get_color_for_value(
        self,
        value: float,
        min_val: float,
        max_val: float,
        colormap: str = "viridis",
    ) -> str:
        """Get color for a value using colormap.

        Args:
            value: Value to map
            min_val: Minimum value
            max_val: Maximum value
            colormap: Colormap name

        Returns:
            Color hex code
        """
        if max_val == min_val:
            normalized = 0.5
        else:
            normalized = (value - min_val) / (max_val - min_val)
            normalized = max(0.0, min(1.0, normalized))

        try:
            cmap = plt.cm.get_cmap(colormap)
        except ValueError:
            # Fallback to viridis
            cmap = plt.cm.get_cmap("viridis")
        rgba = cmap(normalized)
        return matplotlib.colors.rgb2hex(rgba)

    def add_value_labels(
        self,
        ax: Axes,
        bars,
        format_str: str = "{:.2f}",
        offset: float = 0.02,
    ) -> None:
        """Add value labels on top of bars.

        Args:
            ax: Matplotlib axes
            bars: Bar container or list of bars
            format_str: Format string for labels
            offset: Vertical offset as fraction of max value
        """
        if not hasattr(bars, "__iter__"):
            bars = [bars]

        for bar in bars:
            height = bar.get_height()
            max_height = ax.get_ylim()[1]
            label_y = height + offset * max_height

            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                label_y,
                format_str.format(height),
                ha="center",
                va="bottom",
                fontsize=self.theme.font.annotation_size,
            )

    def add_reference_line(
        self,
        ax: Axes,
        value: float,
        orientation: str = "horizontal",
        **kwargs,
    ) -> None:
        """Add reference line (threshold, mean, etc.).

        Args:
            ax: Matplotlib axes
            value: Line value
            orientation: "horizontal" or "vertical"
            **kwargs: Line styling parameters
        """
        color = kwargs.pop("color", "#e74c3c")
        linestyle = kwargs.pop("linestyle", "--")
        linewidth = kwargs.pop("linewidth", 1.5)
        alpha = kwargs.pop("alpha", 0.7)
        label = kwargs.pop("label", None)

        if orientation == "horizontal":
            ax.axhline(
                value,
                color=color,
                linestyle=linestyle,
                linewidth=linewidth,
                alpha=alpha,
                label=label,
                **kwargs,
            )
        else:
            ax.axvline(
                value,
                color=color,
                linestyle=linestyle,
                linewidth=linewidth,
                alpha=alpha,
                label=label,
                **kwargs,
            )


class BaseHeatmapVisualizer(BaseVisualizer):
    """Base class for heatmap visualizations."""

    def __init__(
        self,
        figure_size: tuple[float, float] = (12.0, 8.0),
        dpi: int = 300,
        theme: VisualizationTheme | None = None,
    ):
        """Initialize heatmap visualizer.

        Args:
            figure_size: Figure size
            dpi: DPI
            theme: Visualization theme
        """
        super().__init__(figure_size, dpi, theme)

    def create_heatmap(
        self,
        data: np.ndarray,
        row_labels: list[str],
        col_labels: list[str],
        ax: Axes | None = None,
        colormap: str = "YlOrRd",
        **kwargs,
    ) -> tuple[Figure, Axes]:
        """Create a heatmap.

        Args:
            data: 2D array of data
            row_labels: Row labels
            col_labels: Column labels
            ax: Optional axes (creates new figure if None)
            colormap: Colormap name
            **kwargs: Additional imshow parameters

        Returns:
            Tuple of (figure, axes)
        """
        if ax is None:
            fig, ax = self.create_figure()
        else:
            fig = ax.figure

        im = ax.imshow(data, cmap=colormap, aspect="auto", **kwargs)

        # Set ticks and labels
        ax.set_xticks(np.arange(len(col_labels)))
        ax.set_yticks(np.arange(len(row_labels)))
        ax.set_xticklabels(col_labels, rotation=45, ha="right")
        ax.set_yticklabels(row_labels)

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.ax.tick_params(labelsize=self.theme.font.tick_size)

        return fig, ax
