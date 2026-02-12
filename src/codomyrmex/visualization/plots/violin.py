from typing import List, Any, Optional
import matplotlib.pyplot as plt
import io
import base64
from .base import Plot

class ViolinPlot(Plot):
    """
    Generates a violin plot using Matplotlib.
    Useful for visualizing the distribution of data and its probability density.
    """
    def __init__(self, title: str, data: List[List[float]], labels: List[str] = None):
        super().__init__(title, {"data": data})
        self.labels = labels
        
    def render(self) -> plt.Figure:
        fig, ax = plt.subplots()
        # Create violin plot
        parts = ax.violinplot(self.data["data"], showmeans=False, showmedians=True)
        
        # Customize appearance
        for pc in parts['bodies']:
            pc.set_facecolor('#D43F3A')
            pc.set_edgecolor('black')
            pc.set_alpha(0.7)

        # Set title and labels
        ax.set_title(self.title)
        if self.labels:
            ax.set_xticks(range(1, len(self.labels) + 1))
            ax.set_xticklabels(self.labels)
            
        return fig
    
    def to_html(self) -> str:
        fig = self.render()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return f'<img src="data:image/png;base64,{img_str}" alt="{self.title}">'
