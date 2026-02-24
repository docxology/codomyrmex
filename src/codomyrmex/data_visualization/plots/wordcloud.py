"""WordCloud visualization."""
from ._base import BasePlot


class WordCloud(BasePlot):
    """Word cloud visualization."""

    def __init__(self, title="", words=None, **kwargs):
        """Execute   Init   operations natively."""
        super().__init__(title=title, **kwargs)
        self.words = words or []

    def _render_figure(self, fig, ax):
        """Execute  Render Figure operations natively."""
        if not self.words:
            return
        # Simple scatter representation of words
        for i, (word, size) in enumerate(self.words):
            ax.text(i, 0, word, fontsize=max(8, size), ha="center", va="center")
        ax.set_xlim(-1, len(self.words))
        ax.axis("off")
