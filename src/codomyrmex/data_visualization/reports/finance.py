"""Finance report."""
from pathlib import Path

from ..core.ui import Card, Dashboard
from ._base import BaseReport


class FinanceReport(BaseReport):
    """Finance report with Net Profit and Stock metrics."""

    def __init__(self):
        """Execute   Init   operations natively."""
        super().__init__(title="Financial Overview")
        self.dashboard = Dashboard(title="Financial Overview")
        self._generated = False

    def generate(self) -> None:
        """Generate the finance report content."""
        self.dashboard.add_section("Financial Overview", Card(title="Net Profit", content="$1.2M"))
        self.dashboard.add_section("Stocks", Card(title="CDMX Stock", content="$42.50"))
        self._generated = True

    def save(self, output_path: str) -> str:
        """Generate (if needed) and save the report to a file."""
        if not self._generated:
            self.generate()
        html = self.dashboard.render()
        Path(output_path).write_text(html)
        return str(output_path)
