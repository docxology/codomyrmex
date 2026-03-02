"""Violin plot visualization."""
from ._base import BasePlot


class ViolinPlot(BasePlot):
    """Violin plot visualization."""

    def __init__(self, title="", data=None, labels=None, **kwargs):
        """Initialize this instance."""
        super().__init__(title=title, data=data or [], **kwargs)
        self.labels = labels or []

    def _render_figure(self, fig, ax):
        """render Figure ."""
        if self.data:
            ax.violinplot(self.data)
            if self.labels:
                ax.set_xticks(range(1, len(self.labels) + 1))
                ax.set_xticklabels(self.labels)
