"""Sankey diagram (Mermaid-based)."""
from dataclasses import dataclass, field

from ._base import BasePlot


@dataclass
class SankeyDiagram(BasePlot):
    """Sankey diagram rendered via Mermaid ``sankey-beta`` syntax."""
    links: list = field(default_factory=list)

    def to_html(self) -> str:
        """Override to produce a Mermaid sankey div."""
        lines = ["sankey-beta", ""]
        for src, tgt, val in self.links:
            lines.append(f"{src}, {tgt}, {val}")
        definition = "\n".join(lines)
        return f'<div class="mermaid">{definition}</div>'

    def _render_figure(self, fig, ax):
        """Execute  Render Figure operations natively."""
        ax.text(0.5, 0.5, "Sankey diagram", ha="center", va="center")
