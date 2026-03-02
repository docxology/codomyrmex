"""Pie chart visualization."""
from ._base import BasePlot


class PieChart(BasePlot):
    """Pie chart visualization."""

    def __init__(self, title="", labels=None, sizes=None, **kwargs):
        super().__init__(title=title, **kwargs)
        self.labels = labels or []
        self.sizes = sizes or []

    def _render_figure(self, fig, ax):
        if self.sizes:
            ax.pie(self.sizes, labels=self.labels, autopct="%1.0f%%")
