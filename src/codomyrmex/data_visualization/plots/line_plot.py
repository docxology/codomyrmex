"""Line plot visualization module."""
from ._base import BasePlot


class LinePlot(BasePlot):
    """Line plot visualization.

    Accepts ``x`` / ``y`` keyword arguments or a flat ``data`` list
    (interleaved x, y values).
    """

    def __init__(self, title="", x=None, y=None, data=None, **kwargs):
        """Execute   Init   operations natively."""
        super().__init__(title=title, data=data or [], **kwargs)
        self.x = x or []
        self.y = y or []

    def _render_figure(self, fig, ax):
        """Execute  Render Figure operations natively."""
        if self.x and self.y:
            ax.plot(self.x, self.y)
        elif self.data:
            ax.plot(range(len(self.data)), self.data)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
