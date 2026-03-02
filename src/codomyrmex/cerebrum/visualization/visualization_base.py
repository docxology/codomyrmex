"""Base classes for visualization components."""

from typing import Any

import matplotlib.pyplot as plt
import networkx as nx


class BaseNetworkVisualizer:
    """Base class for network visualizations."""

    def __init__(self, figure_size: tuple[int, int] = (12, 8), dpi: int = 100):
        self.figure_size = figure_size
        self.dpi = dpi

    def create_figure(self) -> tuple[Any, Any]:
        """Create a matplotlib figure and axis."""
        return plt.subplots(figsize=self.figure_size, dpi=self.dpi)

    def apply_layout(self, G: nx.Graph, layout: str = "spring", **kwargs) -> dict:
        """Apply layout to graph."""
        if layout == "spring":
            return nx.spring_layout(G, **kwargs)
        elif layout == "circular":
            return nx.circular_layout(G)
        elif layout == "shell":
            return nx.shell_layout(G)
        else:
            return nx.spring_layout(G, **kwargs)

    def get_node_sizes(self, G: nx.Graph, metric: str = "degree", min_size: int = 100, max_size: int = 1000) -> list:
        """Calculate node sizes based on metric."""
        if metric == "degree":
            degrees = dict(G.degree())
            max_deg = max(degrees.values()) if degrees else 1
            return [min_size + (degrees[n] / max_deg) * (max_size - min_size) for n in G.nodes()]
        return [min_size] * len(G.nodes())

    def get_edge_widths(self, G: nx.Graph, min_width: float = 0.5, max_width: float = 5.0) -> list:
        """Calculate edge widths based on weights."""
        weights = [G[u][v].get("weight", 1) for u, v in G.edges()]
        if not weights:
            return []
        max_w = max(weights)
        return [min_width + (w / max_w) * (max_width - min_width) for w in weights]

    def format_title(self, ax: Any, title: str) -> None:
        """Format plot title."""
        ax.set_title(title, fontsize=16, fontweight="bold")

    def save_figure(self, fig: Any, path: str) -> None:
        """Save figure to path."""
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)


class BaseChartVisualizer:
    """Base class for chart visualizations."""

    def __init__(self, figure_size: tuple[int, int] = (10, 6), dpi: int = 100):
        self.figure_size = figure_size
        self.dpi = dpi

    def create_figure(self) -> tuple[Any, Any]:
        """Create a matplotlib figure and axis."""
        return plt.subplots(figsize=self.figure_size, dpi=self.dpi)

    def format_title(self, ax: Any, title: str) -> None:
        """Format chart title."""
        ax.set_title(title, fontsize=14, fontweight="bold")

    def format_axes_labels(self, ax: Any, xlabel: str, ylabel: str) -> None:
        """Format axis labels."""
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    def add_value_labels(self, ax: Any, rects: Any, format_str: str = "{:.1f}") -> None:
        """Add labels on top of bars."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate(format_str.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')

    def save_figure(self, fig: Any, path: str) -> None:
        """Save figure to path."""
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
