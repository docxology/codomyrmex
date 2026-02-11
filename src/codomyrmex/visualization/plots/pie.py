from typing import List, Any, Optional
import matplotlib.pyplot as plt
import io
import base64
from .base import Plot

class PieChart(Plot):
    """
    Generates a pie chart using Matplotlib.
    """
    def __init__(self, title: str, labels: List[str], sizes: List[float], colors: Optional[List[str]] = None):
        super().__init__(title, {"labels": labels, "sizes": sizes})
        self.colors = colors
        
    def render(self) -> plt.Figure:
        fig, ax = plt.subplots()
        ax.pie(self.data["sizes"], labels=self.data["labels"], autopct='%1.1f%%', startangle=90, colors=self.colors)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
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
