"""General system report."""
from ..core.ui import Card, Dashboard
from ._base import BaseReport


class GeneralSystemReport(BaseReport):
    """General system report."""

    def __init__(self):
        super().__init__(title="Codomyrmex Executive Dashboard")
        self.dashboard = Dashboard(title="Codomyrmex Executive Dashboard")
        self._generated = False

    def generate(self) -> None:
        """Generate the report content."""
        self.dashboard.add_section("Finance: Key Metrics", Card(title="Revenue", content="$2.4M"))
        self.dashboard.add_section("Bio-Sim: Population", Card(title="Colony Size", content="10,000"))
        self.dashboard.add_section("Relations: Social Graph", Card(title="Connections", content="548"))
        self.dashboard.add_section("Education: Learning Path", Card(title="Progress", content="75%"))
        self._generated = True

    def save(self, output_path: str) -> str:
        """Generate (if needed) and save the report to a file."""
        if not self._generated:
            self.generate()
        html = self.dashboard.render()
        from pathlib import Path
        Path(output_path).write_text(html)
        return str(output_path)
