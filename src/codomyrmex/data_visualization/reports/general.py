"""General system report."""
from ..core.ui import Dashboard, Card
from ._base import BaseReport

class GeneralSystemReport(BaseReport):
    """General system report."""
    
    def __init__(self):
        super().__init__()
        self.dashboard = Dashboard(title="Codomyrmex Executive Dashboard")

    def generate(self) -> None:
        """Generate the report content."""
        self.dashboard.add_section("System Status", Card(title="Status", content="Operational"))
        self.dashboard.add_section("Metrics", Card(title="Uptime", content="99.9%"))
