"""Scatter plot visualization."""
from codomyrmex.data_visualization.engines._scatter import apply_scatter

from ._base import BasePlot


class _ScatterPlot(BasePlot):
    """Internal BasePlot-compatible scatter implementation (interleaved flat data list).

    For public use, prefer ``charts.scatter_plot.ScatterPlot`` which accepts
    explicit x_data/y_data arguments.
    """

    def _render_figure(self, fig, ax):
        x = [d for i, d in enumerate(self.data) if i % 2 == 0] or [0]
        y = [d for i, d in enumerate(self.data) if i % 2 == 1] or [0]
        apply_scatter(ax, x, y)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")


# Public alias for backward compatibility — prefer charts.scatter_plot.ScatterPlot
ScatterPlot = _ScatterPlot
