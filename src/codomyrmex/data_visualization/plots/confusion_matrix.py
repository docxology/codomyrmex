"""Confusion matrix visualization."""
import numpy as np

from ._base import BasePlot


class ConfusionMatrix(BasePlot):
    """Confusion matrix visualization."""

    def __init__(self, title="", matrix=None, labels=None, **kwargs):
        super().__init__(title=title, **kwargs)
        self.matrix = matrix or [[0]]
        self.labels = labels or []

    def _render_figure(self, fig, ax):
        arr = np.array(self.matrix)
        ax.imshow(arr, cmap="Blues", aspect="equal")
        n = len(self.labels)
        if n:
            ax.set_xticks(range(n))
            ax.set_xticklabels(self.labels)
            ax.set_yticks(range(n))
            ax.set_yticklabels(self.labels)
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                ax.text(j, i, str(arr[i, j]), ha="center", va="center")
