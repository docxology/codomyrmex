"""Scatter plot functionality for the advanced plotter engine."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from codomyrmex.data_visualization._compat import monitor_performance

if TYPE_CHECKING:
    import matplotlib.pyplot as plt

    from ._types import PlotConfig


class ScatterMixin:
    """Mixin providing scatter plot methods for AdvancedPlotter."""

    config: PlotConfig
    current_axes: plt.Axes | None
    create_figure: callable

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


def create_advanced_scatter_plot(
    x_data: list[float | int | str | datetime],
    y_data: list[float | int | str | datetime],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    config: PlotConfig = None,
    **kwargs,
):
    """Create an advanced scatter plot."""
    from .advanced_plotter import AdvancedPlotter

    plotter = AdvancedPlotter(config)
    plotter.plot_scatter(x_data, y_data, **kwargs)
    return plotter.finalize_plot(title, xlabel, ylabel)
