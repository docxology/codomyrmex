from typing import List, Any, Optional
import matplotlib.pyplot as plt
import io
import base64
from .base import Plot

class AreaPlot(Plot):
    """
    Generates an area plot using Matplotlib.
    """
    def __init__(
        self, 
        title: str, 
        x_data: List[Any], 
        y_data: List[float], 
        x_label: str = "X", 
        y_label: str = "Y",
        color: str = "skyblue",
        alpha: float = 0.4
    ):
        super().__init__(title, {"x": x_data, "y": y_data})
        self.x_label = x_label
        self.y_label = y_label
        self.color = color
        self.alpha = alpha
        
    def render(self) -> plt.Figure:
        fig, ax = plt.subplots()
        ax.fill_between(self.data["x"], self.data["y"], color=self.color, alpha=self.alpha)
        ax.plot(self.data["x"], self.data["y"], color=self.color, alpha=0.6)
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
