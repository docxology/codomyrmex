from typing import List, Tuple, Dict, Any, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64
from .base import Plot

class TreeMap(Plot):
    """
    Generates a Tree Map using Matplotlib.
    Implements a simplified squarified layout algorithm.
    """
    def __init__(self, title: str, data: List[Dict[str, Any]]):
        """
        Args:
            data: List of dicts with 'label' and 'value'.
        """
        # Sort by value descending
        sorted_data = sorted(data, key=lambda x: x['value'], reverse=True)
        super().__init__(title, {"data": sorted_data})
        
    def render(self) -> plt.Figure:
        data = self.data["data"]
        values = [d['value'] for d in data]
        labels = [d['label'] for d in data]
        
        # Normalize values to area 100x100
        total_value = sum(values)
        if total_value == 0:
            return plt.figure()
            
        norm_values = [v / total_value * 100 * 100 for v in values]
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis('off')
        
        rects = self._squarify(norm_values, 0, 0, 100, 100)
        
        colors = plt.cm.Spectral([i/len(rects) for i in range(len(rects))])
        
        for i, rect in enumerate(rects):
            x, y, dx, dy = rect
            color = colors[i]
            # Draw rectangle
            ax.add_patch(patches.Rectangle((x, y), dx, dy, facecolor=color, edgecolor='white'))
            # Add label if it fits
            if dx > 5 and dy > 5:
                ax.text(x + dx/2, y + dy/2, labels[i], ha='center', va='center', color='black', fontsize=8)
                
        ax.set_title(self.title)
        return fig
    
    def _squarify(self, values: List[float], x: float, y: float, w: float, h: float) -> List[Tuple[float, float, float, float]]:
        # Simplified slice-and-dice for robustness
        # Splits either vertically or horizontally based on aspect ratio
        if not values:
            return []
            
        if len(values) == 1:
            return [(x, y, w, h)]
            
        # Split into two groups
        total = sum(values)
        mid = total / 2
        acc = 0
        split_idx = 0
        for i, v in enumerate(values):
            acc += v
            if acc >= mid:
                split_idx = i + 1
                break
                
        group1 = values[:split_idx]
        group2 = values[split_idx:]
        
        total1 = sum(group1)
        total2 = sum(group2)
        
        # Decide split direction
        if w > h:
            # Split vertically (width-wise)
            w1 = (total1 / total) * w
            w2 = w - w1
            return self._squarify(group1, x, y, w1, h) + self._squarify(group2, x + w1, y, w2, h)
        else:
            # Split horizontally (height-wise)
            h1 = (total1 / total) * h
            h2 = h - h1
            # Note: Matplotlib coords start bottom-left. 
            # We stack from bottom to top or top to bottom. Let's do bottom up.
            return self._squarify(group1, x, y, w, h1) + self._squarify(group2, x, y + h1, w, h2)

    def to_html(self) -> str:
        fig = self.render()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return f'<img src="data:image/png;base64,{img_str}" alt="{self.title}">'
