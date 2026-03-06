"""Scatter plot functionality for the advanced plotter engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from codomyrmex.data_visualization._compat import monitor_performance

if TYPE_CHECKING:
    from datetime import datetime

    import matplotlib.pyplot as plt

    from ._types import PlotConfig


class ScatterMixin:
    """Mixin providing scatter plot methods for AdvancedPlotter."""

    config: PlotConfig
    current_axes: plt.Axes | None
    create_figure: callable  # type: ignore

    @monitor_performance("plot_scatter")
    def plot_scatter(
        self,
        x_data: list[float | int | str | datetime],
        y_data: list[float | int | str | datetime],
        label: str = "",
        color: str | None = None,
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

        axes = next(self._iter_axes())

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


def apply_scatter(ax, x_data, y_data, **kwargs):
    """Apply scatter to an axes — canonical delegate; eliminates duplication in charts/ and plots/."""
    return ax.scatter(x_data, y_data, **kwargs)


def create_advanced_scatter_plot(
    x_data: list[float | int | str | datetime],
    y_data: list[float | int | str | datetime],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    config: PlotConfig = None,  # type: ignore
    **kwargs,
):
    """Create an advanced scatter plot."""
    from .advanced_plotter import AdvancedPlotter

    plotter = AdvancedPlotter(config)
    plotter.plot_scatter(x_data, y_data, **kwargs)
    return plotter.finalize_plot(title, xlabel, ylabel)
