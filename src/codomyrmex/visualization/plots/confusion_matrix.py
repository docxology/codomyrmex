from typing import List, Any
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from .base import Plot

class ConfusionMatrix(Plot):
    """
    Generates a Confusion Matrix heatmap.
    """
    def __init__(self, title: str, matrix: List[List[int]], labels: List[str]):
        """
        Args:
            matrix: 2D list of counts.
            labels: Class labels.
        """
        super().__init__(title, {"matrix": matrix, "labels": labels})
        
    def render(self) -> plt.Figure:
        matrix = np.array(self.data["matrix"])
        labels = self.data["labels"]
        
        fig, ax = plt.subplots()
        im = ax.imshow(matrix, interpolation='nearest', cmap=plt.cm.Blues)
        ax.figure.colorbar(im, ax=ax)
        
        # We want to show all ticks...
        ax.set(xticks=np.arange(matrix.shape[1]),
               yticks=np.arange(matrix.shape[0]),
               # ... and label them with the respective list entries
               xticklabels=labels, yticklabels=labels,
               title=self.title,
               ylabel='True label',
               xlabel='Predicted label')

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Loop over data dimensions and create text annotations.
        fmt = 'd'
        thresh = matrix.max() / 2.
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                ax.text(j, i, format(matrix[i, j], fmt),
                        ha="center", va="center",
                        color="white" if matrix[i, j] > thresh else "black")
        
        fig.tight_layout()
        return fig
    
    def to_html(self) -> str:
        fig = self.render()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return f'<img src="data:image/png;base64,{img_str}" alt="{self.title}">'
