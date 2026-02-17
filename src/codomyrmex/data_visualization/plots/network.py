"""Network graph visualization."""
from ._base import BasePlot
import numpy as np


class NetworkGraph(BasePlot):
    """Network graph visualization."""

    def __init__(self, title="", nodes=None, edges=None, **kwargs):
        super().__init__(title=title, **kwargs)
        self.nodes = nodes or []
        self.edges = edges or []

    def _render_figure(self, fig, ax):
        n = len(self.nodes)
        if n == 0:
            return
        # Layout nodes in a circle
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
        x = np.cos(angles)
        y = np.sin(angles)
        node_idx = {name: i for i, name in enumerate(self.nodes)}

        for src, tgt in self.edges:
            si, ti = node_idx.get(src, 0), node_idx.get(tgt, 0)
            ax.plot([x[si], x[ti]], [y[si], y[ti]], "k-", alpha=0.4)

        ax.scatter(x, y, s=200, zorder=5)
        for i, name in enumerate(self.nodes):
            ax.annotate(name, (x[i], y[i]), ha="center", fontsize=9)
        ax.axis("off")
