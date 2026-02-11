from typing import List, Any, Optional
import matplotlib.pyplot as plt
import io
import base64
from .base import Plot

class BoxPlot(Plot):
    """
    Generates a box plot using Matplotlib.
    """
    def __init__(self, title: str, data: List[List[float]], labels: List[str] = None):
        super().__init__(title, {"data": data})
        self.labels = labels
        
    def render(self) -> plt.Figure:
        fig, ax = plt.subplots()
        ax.boxplot(self.data["data"], tick_labels=self.labels)
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
