"""Box plot visualization."""
from ._base import BasePlot


class BoxPlot(BasePlot):
    """Box plot visualization."""

    def __init__(self, title="", data=None, labels=None, **kwargs):
        """Initialize this instance."""
        super().__init__(title=title, data=data or [], **kwargs)
        self.labels = labels or []

    def _render_figure(self, fig, ax):
        """render Figure ."""
        if self.data:
            ax.boxplot(self.data, tick_labels=self.labels or None)
