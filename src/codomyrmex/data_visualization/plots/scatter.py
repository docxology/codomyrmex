"""Scatter plot visualization."""
from ._base import BasePlot


class ScatterPlot(BasePlot):
    """Scatter plot visualization."""

    def _render_figure(self, fig, ax):
        """Execute  Render Figure operations natively."""
        x = [d for i, d in enumerate(self.data) if i % 2 == 0] or [0]
        y = [d for i, d in enumerate(self.data) if i % 2 == 1] or [0]
        ax.scatter(x, y)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
