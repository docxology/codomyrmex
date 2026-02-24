"""Box plot visualization."""
from ._base import BasePlot


class BoxPlot(BasePlot):
    """Box plot visualization."""

    def __init__(self, title="", data=None, labels=None, **kwargs):
        """Execute   Init   operations natively."""
        super().__init__(title=title, data=data or [], **kwargs)
        self.labels = labels or []

    def _render_figure(self, fig, ax):
        """Execute  Render Figure operations natively."""
        if self.data:
            ax.boxplot(self.data, tick_labels=self.labels or None)
