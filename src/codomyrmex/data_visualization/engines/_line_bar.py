"""Line and bar chart functionality for the advanced plotter engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from codomyrmex.data_visualization._compat import monitor_performance

if TYPE_CHECKING:
    from datetime import datetime

    import matplotlib.pyplot as plt

    from ._types import PlotConfig


class LineBarMixin:
    """Mixin providing line and bar plot methods for AdvancedPlotter."""

    config: PlotConfig
    current_axes: plt.Axes | None
    create_figure: callable

    @monitor_performance("plot_line")
    def plot_line(
        self,
        x_data: list[float | int | str | datetime],
        y_data: list[float | int | str | datetime],
        label: str = "",
        color: str | None = None,
        linewidth: float = 2.0,
        linestyle: str = "-",
        marker: str | None = None,
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

    @monitor_performance("plot_bar")
    def plot_bar(
        self,
        x_data: list[str | int | float],
        y_data: list[float | int],
        label: str = "",
        color: str | list[str] | None = None,
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


def create_advanced_line_plot(
    x_data: list[float | int | str | datetime],
    y_data: list[float | int | str | datetime],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    config: PlotConfig = None,
    save_path: str | None = None,
    **kwargs,
):
    """Create an advanced line plot."""
    from .advanced_plotter import AdvancedPlotter

    plotter = AdvancedPlotter(config)
    plotter.plot_line(x_data, y_data, **kwargs)
    return plotter.finalize_plot(title, xlabel, ylabel, save_path=save_path)


def create_advanced_bar_chart(
    x_data: list[str | int | float],
    y_data: list[float | int],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    config: PlotConfig = None,
    save_path: str | None = None,
    **kwargs,
):
    """Create an advanced bar chart."""
    from .advanced_plotter import AdvancedPlotter

    plotter = AdvancedPlotter(config)
    plotter.plot_bar(x_data, y_data, **kwargs)
    return plotter.finalize_plot(title, xlabel, ylabel, save_path=save_path)
