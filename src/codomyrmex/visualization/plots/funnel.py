from typing import List, Any, Optional
import matplotlib.pyplot as plt
import io
import base64
from .base import Plot

class FunnelChart(Plot):
    """
    Generates a funnel chart using Matplotlib (centered horizontal bars).
    Useful for visualizing stages in a process (e.g., sales pipeline).
    """
    def __init__(self, title: str, stages: List[str], values: List[float]):
        super().__init__(title, {"stages": stages, "values": values})
        
    def render(self) -> plt.Figure:
        stages = self.data["stages"]
        values = self.data["values"]
        
        fig, ax = plt.subplots()
        
        y_pos = range(len(stages))
        
        # Draw bars
        # To center them, we can use left = -value/2
        lefts = [-v/2 for v in values]
        ax.barh(y_pos, values, left=lefts, height=0.6, align='center', color='skyblue', edgecolor='black')
        
        # Labels
        ax.set_yticks(y_pos)
        ax.set_yticklabels(stages)
        ax.invert_yaxis() # Top to bottom
        
        # Remove x axis labels as they are relative
        ax.set_xticks([])
        
        # Add value labels
        for i, (v, l) in enumerate(zip(values, lefts)):
            ax.text(0, i, str(v), ha='center', va='center', fontweight='bold')
            
        ax.set_title(self.title)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        return fig
    
    def to_html(self) -> str:
        fig = self.render()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return f'<img src="data:image/png;base64,{img_str}" alt="{self.title}">'
