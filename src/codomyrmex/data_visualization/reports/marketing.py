"""Marketing report."""
from pathlib import Path

from ..core.ui import Dashboard, Card
from ._base import BaseReport


class MarketingReport(BaseReport):
    """Marketing report with Brand Awareness and User Acquisition metrics."""

    def __init__(self):
        super().__init__(title="Marketing Analysis")
        self.dashboard = Dashboard(title="Marketing Analysis")
        self._generated = False

    def generate(self) -> None:
        """Generate the marketing report content."""
        self.dashboard.add_section("Marketing Analysis", Card(title="Brand Awareness", content="78%"))
        self.dashboard.add_section("Acquisition", Card(title="User Acquisition", content="12,500 new users"))
        self._generated = True

    def save(self, output_path: str) -> str:
        """Generate (if needed) and save the report to a file."""
        if not self._generated:
            self.generate()
        html = self.dashboard.render()
        Path(output_path).write_text(html)
        return str(output_path)
