"""Funnel chart visualization."""
from ._base import BasePlot


class FunnelChart(BasePlot):
    """Funnel chart visualization."""

    def __init__(self, title="", stages=None, values=None, **kwargs):
        """Execute   Init   operations natively."""
        super().__init__(title=title, **kwargs)
        self.stages = stages or []
        self.funnel_values = values or []

    def _render_figure(self, fig, ax):
        """Execute  Render Figure operations natively."""
        n = len(self.stages)
        for i in range(n):
            ax.barh(n - i - 1, self.funnel_values[i], align="center")
            ax.text(self.funnel_values[i] / 2, n - i - 1, self.stages[i],
                    ha="center", va="center", fontsize=9)
        ax.set_yticks([])
        ax.set_xlabel("Count")
