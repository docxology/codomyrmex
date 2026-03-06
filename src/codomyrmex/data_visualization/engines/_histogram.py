"""Histogram, box, and violin plot functionality for the advanced plotter engine."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd
import seaborn as sns

from codomyrmex.data_visualization._compat import monitor_performance

if TYPE_CHECKING:
    import matplotlib.pyplot as plt

    from ._types import PlotConfig


class HistogramMixin:
    """Mixin providing histogram, box, and violin methods for AdvancedPlotter."""

    config: PlotConfig
    current_axes: plt.Axes | None
    create_figure: callable  # type: ignore

    @monitor_performance("plot_histogram")
    def plot_histogram(
        self,
        data: list[float | int],
        bins: int | list[float] = 30,
        label: str = "",
        color: str | None = None,
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

    @monitor_performance("plot_box")
    def plot_box(
        self,
        data: list[float | int] | dict[str, list[float | int]],
        labels: list[str] | None = None,
        color: str | list[str] | None = None,
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
            data_list, tick_labels=labels, notch=notch, patch_artist=patch_artist, **kwargs
        )

        if color and patch_artist:
            if isinstance(color, str):
                color = [color] * len(data_list)
            for patch, col in zip(box_plot["boxes"], color, strict=False):
                patch.set_facecolor(col)

        return box_plot

    @monitor_performance("plot_violin")
    def plot_violin(
        self,
        data: list[float | int] | dict[str, list[float | int]],
        labels: list[str] | None = None,
        color: str | list[str] | None = None,
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


def create_advanced_histogram(
    data: list[float | int],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    config: PlotConfig = None,  # type: ignore
    **kwargs,
):
    """Create an advanced histogram."""
    from .advanced_plotter import AdvancedPlotter

    plotter = AdvancedPlotter(config)
    plotter.plot_histogram(data, **kwargs)
    return plotter.finalize_plot(title, xlabel, ylabel)
