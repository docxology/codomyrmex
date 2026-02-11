from abc import ABC, abstractmethod
from ..core.dashboard import Dashboard

class Report(ABC):
    """
    Abstract base class for domain-specific reports.
    """
    def __init__(self, title: str):
        self.dashboard = Dashboard(title=title)
        
    @abstractmethod
    def generate(self) -> None:
        """
        Populates the dashboard with data/plots.
        """
        pass
        
    def save(self, output_path: str) -> str:
        """
        Generates and saves the report.
        """
        self.generate()
        return self.dashboard.render(output_path)
