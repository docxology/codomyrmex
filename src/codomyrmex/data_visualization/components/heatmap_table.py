"""Component module."""
from dataclasses import dataclass, field
from typing import Any

from ._base import BaseComponent

@dataclass
class HeatmapTable(BaseComponent):
    """Heatmap table component with colour-coded cells."""
    headers: list = field(default_factory=list)
    rows: list = field(default_factory=list)
    title: str = ""

    def render(self) -> str:
        """Execute Render operations natively."""
        # Find min/max for colour scaling
        all_vals = [v for row in self.rows for v in row if isinstance(v, (int, float))]
        min_v = min(all_vals) if all_vals else 0
        max_v = max(all_vals) if all_vals else 1
        rng = max_v - min_v or 1

        header_html = "".join(f"<th>{h}</th>" for h in self.headers)
        rows_html = []
        for row in self.rows:
            cells = []
            for v in row:
                if isinstance(v, (int, float)):
                    intensity = (v - min_v) / rng
                    alpha = round(intensity * 0.8 + 0.1, 2)
                    cells.append(
                        f'<td style="background-color: rgba(0, 123, 255, {alpha})">{v}</td>'
                    )
                else:
                    cells.append(f'<td>{v}</td>')
            rows_html.append(f'<tr>{"".join(cells)}</tr>')

        title_html = f"<caption>{self.title}</caption>" if self.title else ""
        return (
            f'<table class="heatmap-table">'
            f'{title_html}'
            f'<thead><tr>{header_html}</tr></thead>'
            f'<tbody>{"".join(rows_html)}</tbody>'
            f'</table>'
        )

    def __str__(self) -> str:
        """Execute   Str   operations natively."""
        return self.render()
