from typing import List, Any, Optional
import matplotlib.pyplot as plt
import io
import base64
from .base import Plot

class Histogram(Plot):
    """
    Generates a histogram using Matplotlib.
    """
    def __init__(self, title: str, data: List[float], bins: int = 10, x_label: str = "Value", y_label: str = "Frequency", color: str = None):
        super().__init__(title, {"data": data, "bins": bins})
        self.x_label = x_label
        self.y_label = y_label
        self.color = color
        
    def render(self) -> plt.Figure:
        fig, ax = plt.subplots()
        ax.hist(self.data["data"], bins=self.data["bins"], color=self.color, edgecolor='black')
        ax.set_title(self.title)
        ax.set_xlabel(self.x_label)
        ax.set_ylabel(self.y_label)
        return fig
    
    def to_html(self) -> str:
        fig = self.render()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return f'<img src="data:image/png;base64,{img_str}" alt="{self.title}">'
