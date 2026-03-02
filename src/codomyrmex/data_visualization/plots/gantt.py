"""Gantt chart visualization."""
from ._base import BasePlot


class GanttChart(BasePlot):
    """Gantt chart visualization."""

    def __init__(self, title="", tasks=None, starts=None, durations=None, **kwargs):
        super().__init__(title=title, **kwargs)
        self.tasks = tasks or []
        self.starts = starts or []
        self.durations = durations or []

    def _render_figure(self, fig, ax):
        n = len(self.tasks)
        for i in range(n):
            ax.barh(i, self.durations[i], left=self.starts[i])
        ax.set_yticks(range(n))
        ax.set_yticklabels(self.tasks)
        ax.set_xlabel("Time")
