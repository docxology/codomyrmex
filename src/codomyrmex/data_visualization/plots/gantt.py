"""Gantt chart visualization."""
from ._base import BasePlot


class GanttChart(BasePlot):
    """Gantt chart visualization."""

    def __init__(self, title="", tasks=None, starts=None, durations=None, **kwargs):
        """Execute   Init   operations natively."""
        super().__init__(title=title, **kwargs)
        self.tasks = tasks or []
        self.starts = starts or []
        self.durations = durations or []

    def _render_figure(self, fig, ax):
        """Execute  Render Figure operations natively."""
        n = len(self.tasks)
        for i in range(n):
            ax.barh(i, self.durations[i], left=self.starts[i])
        ax.set_yticks(range(n))
        ax.set_yticklabels(self.tasks)
        ax.set_xlabel("Time")
