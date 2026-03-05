"""Dashboard creation functionality for the advanced plotter engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from codomyrmex.data_visualization._compat import monitor_performance

from ._types import Dataset, PlotType

if TYPE_CHECKING:
    from ._types import PlotConfig


class DashboardMixin:
    """Mixin providing dashboard creation methods for AdvancedPlotter."""

    config: PlotConfig
    create_figure: callable

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
        else:
            axes = axes.flatten()

        for i, dataset in enumerate(datasets):
            if i >= len(axes):
                break

            ax = axes[i]
            _plot_dataset(ax, dataset)

        # Hide unused subplots
        for i in range(len(datasets), len(axes)):
            axes[i].set_visible(False)

        fig.suptitle(title, fontsize=16, fontweight="bold")

        if self.config.tight_layout:
            fig.tight_layout()

        return fig


def _plot_dataset(ax: plt.Axes, dataset: Dataset):
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


def create_advanced_dashboard(
    datasets: list[Dataset],
    title: str = "Dashboard",
    layout: tuple[int, int] = (2, 2),
    config: PlotConfig = None,
    **kwargs,
):
    """Create an advanced dashboard."""
    from .advanced_plotter import AdvancedPlotter

    plotter = AdvancedPlotter(config)
    return plotter.create_dashboard(datasets, layout, title, **kwargs)
