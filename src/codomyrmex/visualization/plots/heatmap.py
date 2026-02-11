from typing import List, Any, Union
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from .base import Plot

class Heatmap(Plot):
    """
    Generates a heatmap using Matplotlib.
    """
    def __init__(self, title: str, data: List[List[float]], x_labels: List[str] = None, y_labels: List[str] = None):
        super().__init__(title, data)
        self.x_labels = x_labels
        self.y_labels = y_labels
        
    def render(self) -> plt.Figure:
        data_np = np.array(self.data)
        fig, ax = plt.subplots()
        im = ax.imshow(data_np)
        
        ax.set_title(self.title)
        
        if self.x_labels:
            ax.set_xticks(np.arange(len(self.x_labels)), labels=self.x_labels)
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            
        if self.y_labels:
            ax.set_yticks(np.arange(len(self.y_labels)), labels=self.y_labels)

        # Create colorbar
        fig.colorbar(im, ax=ax)
        fig.tight_layout()
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
        plt.close(fig)
        return f'<img src="data:image/png;base64,{img_str}" alt="{self.title}">'
