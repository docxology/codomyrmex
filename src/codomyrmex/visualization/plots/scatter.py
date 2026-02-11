from typing import List, Any
import matplotlib.pyplot as plt
import io
import base64
from .base import Plot

class ScatterPlot(Plot):
    """
    Generates a scatter plot using Matplotlib.
    """
    def __init__(self, title: str, x_data: List[float], y_data: List[float], x_label: str = "X", y_label: str = "Y"):
        super().__init__(title, {"x": x_data, "y": y_data})
        self.x_label = x_label
        self.y_label = y_label
        
    def render(self) -> plt.Figure:
        fig, ax = plt.subplots()
        ax.scatter(self.data["x"], self.data["y"])
        ax.set_title(self.title)
        ax.set_xlabel(self.x_label)
        ax.set_ylabel(self.y_label)
        return fig
    
    def to_html(self) -> str:
        """
        Renders the matplotlib figure to a base64 encoded PNG for HTML embedding.
        """
        fig = self.render()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig) # Close to free memory
        return f'<img src="data:image/png;base64,{img_str}" alt="{self.title}">'
