"""Radar chart visualization."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np

from ._base import BasePlot


class RadarChart(BasePlot):
    """Radar / spider chart visualization.

    Overrides ``to_html()`` directly because radar charts require a polar axes
    which cannot be created from within ``_render_figure`` (the base factory
    creates a cartesian axes).
    """

    def __init__(self, title="", categories=None, values=None, **kwargs):
        """Initialize this instance."""
        super().__init__(title=title, **kwargs)
        self.categories = categories or []
        self.values = values or []

    def to_html(self) -> str:
        """Override to produce a polar radar chart."""
        n = len(self.categories)
        fig = plt.figure(figsize=(self.width / 100, self.height / 100), dpi=100)
        ax = fig.add_subplot(111, polar=True)

        if n > 0:
            angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
            vals = list(self.values) + [self.values[0]]
            angles += angles[:1]
            ax.plot(angles, vals)
            ax.fill(angles, vals, alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(self.categories)

        ax.set_title(self.title)
        fig.tight_layout()

        png = self._fig_to_base64(fig)
        plt.close(fig)
        return f'<img src="data:image/png;base64,{png}" alt="{self.title}" />'
