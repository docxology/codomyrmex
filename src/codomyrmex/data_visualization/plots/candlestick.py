"""Candlestick chart visualization."""
from ._base import BasePlot


class CandlestickChart(BasePlot):
    """Candlestick / OHLC chart visualization."""

    def __init__(self, title="", dates=None, opens=None, highs=None, lows=None, closes=None, **kwargs):
        super().__init__(title=title, **kwargs)
        self.dates = dates or []
        self.opens = opens or []
        self.highs = highs or []
        self.lows = lows or []
        self.closes = closes or []

    def _render_figure(self, fig, ax):
        n = len(self.dates)
        for i in range(n):
            colour = "green" if self.closes[i] >= self.opens[i] else "red"
            ax.plot([i, i], [self.lows[i], self.highs[i]], color="black", linewidth=0.5)
            ax.bar(i, self.closes[i] - self.opens[i], bottom=self.opens[i],
                   color=colour, width=0.6)
        ax.set_xticks(range(n))
        ax.set_xticklabels(self.dates, rotation=45, fontsize=7)
