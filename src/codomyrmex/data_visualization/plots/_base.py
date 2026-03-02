"""Base class for all plot types.

Provides ``to_html()`` which renders the plot data as a matplotlib figure
encoded as an inline base64 PNG ``<img>`` tag.  Subclasses should override
``_render_figure(fig, ax)`` to customise the matplotlib drawing.
"""
from __future__ import annotations

import base64
import io
from dataclasses import dataclass, field
from typing import Any

import matplotlib

matplotlib.use("Agg")          # non-interactive backend
import matplotlib.pyplot as plt  # noqa: E402


@dataclass
class BasePlot:
    """Base class for all plot types.

    Attributes:
        title: Chart title rendered in the axes.
        width: Width of the figure in pixels.
        height: Height of the figure in pixels.
        data: Generic data container used by subclasses.
        options: Additional rendering options.
    """
    title: str = ""
    width: int = 800
    height: int = 400
    data: list[Any] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)

    # ──────────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────────
    def render(self) -> str:
        """Return a simple HTML placeholder div."""
        return f'<div class="plot" data-type="{self.__class__.__name__}">{self.title}</div>'

    def to_html(self) -> str:
        """Render the plot as an ``<img>`` tag containing a base64 PNG."""
        fig, ax = plt.subplots(
            figsize=(self.width / 100, self.height / 100), dpi=100
        )
        self._render_figure(fig, ax)
        ax.set_title(self.title)
        fig.tight_layout()
        png = self._fig_to_base64(fig)
        plt.close(fig)
        return f'<img src="data:image/png;base64,{png}" alt="{self.title}" />'

    def to_dict(self) -> dict[str, Any]:
        """Serialize plot metadata to a dictionary."""
        return {
            "type": self.__class__.__name__,
            "title": self.title,
            "width": self.width,
            "height": self.height,
            "data_count": len(self.data),
        }

    def save(self, output_path: str) -> str:
        """Save the rendered plot HTML to a file.

        Args:
            output_path: File path to save the HTML.

        Returns:
            The *output_path* for chaining convenience.
        """
        from pathlib import Path
        html = self.to_html()
        Path(output_path).write_text(
            f"<!DOCTYPE html><html><body>{html}</body></html>"
        )
        return output_path

    def __str__(self) -> str:
        """str ."""
        return self.to_html()

    def __repr__(self) -> str:
        """repr ."""
        return f"{self.__class__.__name__}(title={self.title!r}, data_count={len(self.data)})"

    # ──────────────────────────────────────────────
    #  Extension point for subclasses
    # ──────────────────────────────────────────────
    def _render_figure(self, fig: Any, ax: Any) -> None:
        """Override in subclasses to draw on *ax*."""
        ax.text(0.5, 0.5, self.title, ha="center", va="center", fontsize=14)

    # ──────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────
    @staticmethod
    def _fig_to_base64(fig: Any) -> str:
        """Convert a matplotlib figure to a base64-encoded PNG string."""
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("ascii")
