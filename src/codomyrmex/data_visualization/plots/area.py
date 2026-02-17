"""Area plot visualization."""
from ._base import BasePlot


class AreaPlot(BasePlot):
    """Area plot visualization."""

    def __init__(self, title="", x=None, y=None, **kwargs):
        super().__init__(title=title, **kwargs)
        self.x = x or []
        self.y = y or []

    def _render_figure(self, fig, ax):
        if self.x and self.y:
            ax.fill_between(self.x, self.y, alpha=0.5)
            ax.plot(self.x, self.y)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
