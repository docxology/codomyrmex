"""Logistics report."""
from pathlib import Path

from codomyrmex.data_visualization.core.ui import Card, Dashboard
from codomyrmex.data_visualization.plots.sankey import SankeyDiagram

from ._base import BaseReport


class LogisticsReport(BaseReport):
    """Logistics report with shipment tracking and goods-flow Sankey diagram."""

    def __init__(self):
        super().__init__(title="Logistics & Operations")
        self.dashboard = Dashboard(title="Logistics & Operations")
        self._generated = False

    def generate(self) -> None:
        """Generate the logistics report content."""
        self.dashboard.add_section(
            "Logistics & Operations",
            Card(title="Shipment #1234", content="In Transit"),
        )
        sankey = SankeyDiagram(
            title="Goods Flow",
            links=[("Warehouse", "Distribution", 50), ("Distribution", "Retail", 30)],
        )
        self.dashboard.add_section("Goods Flow", sankey.to_html())
        self._generated = True

    def save(self, output_path: str) -> str:
        """Generate (if needed) and save the report to a file."""
        if not self._generated:
            self.generate()
        html = self.dashboard.render()
        Path(output_path).write_text(html)
        return str(output_path)
