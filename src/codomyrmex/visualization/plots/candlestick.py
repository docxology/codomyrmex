from typing import List, Any, Tuple
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import io
import base64
from .base import Plot

class CandlestickChart(Plot):
    """
    Generates a candlestick chart for financial data using Matplotlib.
    Does NOT require mplfinance to minimize dependencies.
    """
    def __init__(self, title: str, dates: List[str], opens: List[float], highs: List[float], lows: List[float], closes: List[float]):
        """
        Args:
            dates: List of date strings or indices.
            opens: Opening prices.
            highs: High prices.
            lows: Low prices.
            closes: Closing prices.
        """
        data = {
            "dates": dates,
            "opens": opens,
            "highs": highs,
            "lows": lows,
            "closes": closes
        }
        super().__init__(title, data)
        
    def render(self) -> plt.Figure:
        dates = self.data["dates"]
        opens = self.data["opens"]
        highs = self.data["highs"]
        lows = self.data["lows"]
        closes = self.data["closes"]
        
        fig, ax = plt.subplots()
        
        width = 0.5
        width2 = 0.05
        
        up_color = 'green'
        down_color = 'red'
        
        for i in range(len(dates)):
            open_val = opens[i]
            close_val = closes[i]
            high_val = highs[i]
            low_val = lows[i]
            
            color = up_color if close_val >= open_val else down_color
            
            # Draw the wick (high to low)
            ax.plot([i, i], [low_val, high_val], color='black', linewidth=1)
            
            # Draw the body
            rect = Rectangle((i - width/2, min(open_val, close_val)), width, abs(close_val - open_val), facecolor=color, edgecolor='black')
            ax.add_patch(rect)
            
        ax.set_title(self.title)
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=45, ha='right')
        ax.set_ylabel("Price")
        ax.autoscale_view()
        
        return fig
    
    def to_html(self) -> str:
        fig = self.render()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return f'<img src="data:image/png;base64,{img_str}" alt="{self.title}">'
