"""Heatmap and correlation plot functionality for the advanced plotter engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import seaborn as sns

from codomyrmex.data_visualization._compat import monitor_performance

if TYPE_CHECKING:
    import matplotlib.pyplot as plt

    from ._types import PlotConfig


class HeatmapMixin:
    """Mixin providing heatmap and correlation methods for AdvancedPlotter."""

    config: PlotConfig
    current_axes: plt.Axes | None
    create_figure: callable

    @monitor_performance("plot_heatmap")
    def plot_heatmap(
        self,
        data: list[list[float]] | np.ndarray | pd.DataFrame,
        x_labels: list[str] | None = None,
        y_labels: list[str] | None = None,
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
            xticklabels=x_labels if x_labels is not None else "auto",
            yticklabels=y_labels if y_labels is not None else "auto",
            cmap=cmap,
            annot=annot,
            fmt=fmt,
            cbar=cbar,
            ax=axes,
            **kwargs,
        )

        return heatmap

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


def create_advanced_heatmap(
    data: list[list[float]] | np.ndarray | pd.DataFrame,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    config: PlotConfig = None,
    **kwargs,
):
    """Create an advanced heatmap."""
    from .advanced_plotter import AdvancedPlotter

    plotter = AdvancedPlotter(config)
    plotter.plot_heatmap(data, **kwargs)
    return plotter.finalize_plot(title, xlabel, ylabel)
