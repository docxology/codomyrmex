"""
Data Lineage Module Implementation

Core class for data lineage tracking and analysis.
"""

from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .graph import LineageGraph
from .tracker import ImpactAnalyzer, LineageTracker

logger = get_logger(__name__)


class DataLineage:
    """Main class for data lineage functionality."""

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize DataLineage.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.graph = LineageGraph()
        self.tracker = LineageTracker(self.graph)
        self.analyzer = ImpactAnalyzer(self.graph)
        logger.info("DataLineage initialized")

    def track(self, event_type: str, **kwargs) -> Any:
        """
        Track a lineage event.

        Args:
            event_type: Type of event ('dataset' or 'transformation')
            **kwargs: Arguments for registration methods
        """
        if event_type == "dataset":
            return self.tracker.register_dataset(**kwargs)
        elif event_type == "transformation":
            return self.tracker.register_transformation(**kwargs)
        else:
            raise ValueError(f"Unknown event type: {event_type}")

    def analyze(self, node_id: str) -> dict[str, Any]:
        """Analyze impact of a node."""
        return self.analyzer.analyze_change(node_id)


# Convenience function
def create_data_lineage(config: dict[str, Any] | None = None) -> DataLineage:
    """
    Create a new DataLineage instance.

    Args:
        config: Optional configuration

    Returns:
        DataLineage instance
    """
    return DataLineage(config)
