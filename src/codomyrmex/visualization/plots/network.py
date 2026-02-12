from typing import List, Tuple, Dict, Optional
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from .base import Plot

class NetworkGraph(Plot):
    """
    Generates a Network Graph (node-link diagram) using Matplotlib.
    Defaults to circular layout if no positions are provided.
    """
    def __init__(self, title: str, nodes: List[str], edges: List[Tuple[str, str]], positions: Optional[Dict[str, Tuple[float, float]]] = None):
        """
        Args:
            nodes: List of node IDs.
            edges: List of (source, target) tuples.
            positions: Optional dict of node_id -> (x, y).
        """
        super().__init__(title, {"nodes": nodes, "edges": edges, "positions": positions})
        
    def render(self) -> plt.Figure:
        nodes = self.data["nodes"]
        edges = self.data["edges"]
        positions = self.data["positions"]
        
        # Calculate positions if not provided (Circular Layout)
        if not positions:
            positions = {}
            n = len(nodes)
            for i, node in enumerate(nodes):
                angle = 2 * np.pi * i / n
                positions[node] = (np.cos(angle), np.sin(angle))
                
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_axis_off()
        
        # Draw edges
        for u, v in edges:
            if u in positions and v in positions:
                x1, y1 = positions[u]
                x2, y2 = positions[v]
                ax.plot([x1, x2], [y1, y2], 'k-', alpha=0.3, zorder=1)
                
        # Draw nodes
        for node in nodes:
            x, y = positions[node]
            ax.scatter(x, y, s=500, c='skyblue', edgecolors='black', zorder=2)
            ax.text(x, y, node, ha='center', va='center', zorder=3, fontsize=9)
            
        ax.set_title(self.title)
        return fig
    
    def to_html(self) -> str:
        fig = self.render()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return f'<img src="data:image/png;base64,{img_str}" alt="{self.title}">'
