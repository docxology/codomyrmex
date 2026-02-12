from typing import List, Any, Optional
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from .base import Plot

class RadarChart(Plot):
    """
    Generates a radar chart (spider plot) using Matplotlib.
    Useful for comparing multiple quantitative variables.
    """
    def __init__(self, title: str, categories: List[str], values: List[float], max_val: Optional[float] = None):
        super().__init__(title, {"categories": categories, "values": values})
        self.max_val = max_val
        
    def render(self) -> plt.Figure:
        categories = self.data["categories"]
        values = self.data["values"]
        N = len(categories)

        # Compute angle for each axis
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1] # Close the loop
        
        values += values[:1] # Close the loop
        
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        
        ax.plot(angles, values, linewidth=1, linestyle='solid')
        ax.fill(angles, values, 'b', alpha=0.1)
        
        # Set category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        
        if self.max_val:
            ax.set_ylim(0, self.max_val)
            
        ax.set_title(self.title, y=1.1)
        
        return fig
    
    def to_html(self) -> str:
        fig = self.render()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return f'<img src="data:image/png;base64,{img_str}" alt="{self.title}">'
