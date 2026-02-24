"""Bar chart visualization module."""
from ._base import BasePlot


class BarChart(BasePlot):
    """Bar chart visualization.

    Accepts data as a list of ``(label, value)`` tuples or via
    ``categories`` / ``values`` keyword arguments.
    """

    def __init__(self, title="", data=None, categories=None, values=None, **kwargs):
        """Execute   Init   operations natively."""
        super().__init__(title=title, data=data or [], **kwargs)
        self.categories = categories or []
        self.values = values or []

    def _render_figure(self, fig, ax):
        """Execute  Render Figure operations natively."""
        if self.categories and self.values:
            ax.bar(self.categories, self.values)
        elif self.data:
            labels = [str(d[0]) if isinstance(d, (list, tuple)) else str(i) for i, d in enumerate(self.data)]
            vals = [d[1] if isinstance(d, (list, tuple)) else d for d in self.data]
            ax.bar(labels, vals)
        ax.set_xlabel("Category")
        ax.set_ylabel("Value")
