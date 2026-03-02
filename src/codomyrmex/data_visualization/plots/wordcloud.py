"""WordCloud visualization."""
from ._base import BasePlot


class WordCloud(BasePlot):
    """Word cloud visualization."""

    def __init__(self, title="", words=None, **kwargs):
        """Initialize this instance."""
        super().__init__(title=title, **kwargs)
        self.words = words or []

    def _render_figure(self, fig, ax):
        """render Figure ."""
        if not self.words:
            return
        # Simple scatter representation of words
        for i, (word, size) in enumerate(self.words):
            ax.text(i, 0, word, fontsize=max(8, size), ha="center", va="center")
        ax.set_xlim(-1, len(self.words))
        ax.axis("off")
