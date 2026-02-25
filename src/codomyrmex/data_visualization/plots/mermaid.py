"""Mermaid diagram wrapper."""
from dataclasses import dataclass

from ._base import BasePlot


@dataclass
class MermaidDiagram(BasePlot):
    """Mermaid diagram wrapper — renders as an inline ``<div class="mermaid">`` block."""
    definition: str = ""

    def to_html(self) -> str:
        """Override to produce a Mermaid div instead of a PNG image."""
        return f'<div class="mermaid">{self.definition}</div>'

    def _render_figure(self, fig, ax):
        """Execute  Render Figure operations natively."""
        ax.text(0.5, 0.5, "Mermaid diagram", ha="center", va="center")
