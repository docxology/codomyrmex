from typing import List, Any
import matplotlib.pyplot as plt
import io
import base64
from .base import Plot

class BarPlot(Plot):
    """
    Generates a bar plot using Matplotlib.
    """
    def __init__(self, title: str, categories: List[str], values: List[float], x_label: str = "Category", y_label: str = "Value"):
        super().__init__(title, {"x": categories, "y": values})
        self.x_label = x_label
        self.y_label = y_label
        
    def render(self) -> plt.Figure:
        fig, ax = plt.subplots()
        ax.bar(self.data["x"], self.data["y"])
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
