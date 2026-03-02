"""Histogram visualization."""
from ._base import BasePlot


class Histogram(BasePlot):
    """Histogram visualization."""

    def __init__(self, title="", data=None, bins=10, **kwargs):
        """Initialize this instance."""
        super().__init__(title=title, data=data or [], **kwargs)
        self.bins = bins

    def _render_figure(self, fig, ax):
        """render Figure ."""
        if self.data:
            ax.hist(self.data, bins=self.bins)
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")
