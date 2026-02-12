from typing import List, Any, Tuple
import matplotlib.pyplot as plt
import io
import base64
from .base import Plot

class GanttChart(Plot):
    """
    Generates a Gantt chart for project scheduling.
    """
    def __init__(self, title: str, tasks: List[str], start_dates: List[float], durations: List[float]):
        """
        Args:
            tasks: Task names.
            start_dates: Start time (numerical, e.g., day number).
            durations: Duration of task.
        """
        super().__init__(title, {"tasks": tasks, "starts": start_dates, "durations": durations})
        
    def render(self) -> plt.Figure:
        fig, ax = plt.subplots()
        
        tasks = self.data["tasks"]
        starts = self.data["starts"]
        durations = self.data["durations"]
        
        # Invert Y axis so first task is at top
        y_pos = range(len(tasks))
        
        ax.barh(y_pos, durations, left=starts, align='center', color='skyblue')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(tasks)
        ax.invert_yaxis() 
        ax.set_xlabel('Time')
        ax.set_title(self.title)
        
        return fig
    
    def to_html(self) -> str:
        fig = self.render()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return f'<img src="data:image/png;base64,{img_str}" alt="{self.title}">'
