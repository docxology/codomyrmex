"""TreeMap visualization."""
from ._base import BasePlot


class TreeMap(BasePlot):
    """Treemap visualization."""

    def __init__(self, title="", data=None, **kwargs):
        """Execute   Init   operations natively."""
        super().__init__(title=title, data=data or [], **kwargs)

    def _render_figure(self, fig, ax):
        """Execute  Render Figure operations natively."""
        if not self.data:
            return
        labels = [d.get("label", "") for d in self.data]
        values = [d.get("value", 0) for d in self.data]
        ax.barh(labels, values)
        ax.set_xlabel("Value")
