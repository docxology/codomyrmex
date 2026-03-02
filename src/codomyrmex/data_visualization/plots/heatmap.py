"""Heatmap visualization."""
from ._base import BasePlot


class Heatmap(BasePlot):
    """Heatmap visualization."""

    def _render_figure(self, fig, ax):
        """render Figure ."""
        matrix = self.data if self.data else [[0]]
        ax.imshow(matrix, aspect="auto", cmap="viridis")
        ax.set_xlabel("Columns")
        ax.set_ylabel("Rows")
