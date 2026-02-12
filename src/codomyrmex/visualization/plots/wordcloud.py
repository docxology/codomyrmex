from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
import random
import io
import base64
from .base import Plot

class WordCloud(Plot):
    """
    Generates a simple Word Cloud using Matplotlib.
    Zero-dependency implementation (does not use wordcloud library).
    """
    def __init__(self, title: str, words: List[Tuple[str, float]]):
        """
        Args:
            words: List of (word, frequency) tuples.
        """
        super().__init__(title, {"words": words})
        
    def render(self) -> plt.Figure:
        words = self.data["words"]
        # Normalize sizes
        if not words:
            return plt.figure()
            
        max_freq = max(w[1] for w in words)
        min_freq = min(w[1] for w in words)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis('off')
        
        # Simple random placement strategy
        # In a real implementation without 'wordcloud' lib, collision detection is hard.
        # We will just place them randomly for this basic version.
        
        placed_rects = []
        
        colors = ['#2c3e50', '#e74c3c', '#3498db', '#f1c40f', '#27ae60']
        
        for word, freq in words:
            # Scale font size
            if max_freq == min_freq:
                size = 20
            else:
                size = 10 + (freq - min_freq) / (max_freq - min_freq) * 40
            
            x = random.randint(10, 90)
            y = random.randint(10, 90)
            color = random.choice(colors)
            
            ax.text(x, y, word, fontsize=size, color=color, ha='center', va='center', alpha=0.8)
            
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
