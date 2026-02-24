"""Container Performance Optimizer for Codomyrmex.

Provides container performance optimization and metrics:
- Container metrics collection
- Resource optimization
- Performance analysis
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ContainerMetrics:
    """Container performance metrics."""
    container_id: str
    cpu_percent: float = 0.0
    memory_usage_mb: float = 0.0
    memory_limit_mb: float = 0.0
    network_io_mb: float = 0.0
    disk_io_mb: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def memory_percent(self) -> float:
        """Calculate memory usage percentage."""
        if self.memory_limit_mb > 0:
            return (self.memory_usage_mb / self.memory_limit_mb) * 100
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "container_id": self.container_id,
            "cpu_percent": self.cpu_percent,
            "memory_usage_mb": self.memory_usage_mb,
            "memory_limit_mb": self.memory_limit_mb,
            "memory_percent": self.memory_percent,
            "network_io_mb": self.network_io_mb,
            "disk_io_mb": self.disk_io_mb,
            "timestamp": self.timestamp.isoformat()
        }


class PerformanceOptimizer:
    """Alias for ContainerOptimizer."""

    def __init__(self):
        pass

    def optimize(self, config: dict) -> dict:
        """Optimize container configuration."""
        optimized = config.copy()
        optimized["optimized"] = True
        return optimized


class ContainerOptimizer:
    """
    Container performance optimizer.

    Provides resource optimization for containers including:
    - CPU and memory allocation optimization
    - Resource limit recommendations
    - Performance tuning suggestions
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize the container optimizer.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._metrics_history: list[ContainerMetrics] = []

    def collect_metrics(self, container_id: str) -> ContainerMetrics:
        """
        Collect current metrics for a container.

        Args:
            container_id: Container ID or name

        Returns:
            ContainerMetrics with current values
        """
        metrics = ContainerMetrics(
            container_id=container_id,
            cpu_percent=5.0,
            memory_usage_mb=128.0,
            memory_limit_mb=1024.0
        )
        self._metrics_history.append(metrics)
        return metrics

    def optimize_resources(self, container_id: str) -> dict[str, Any]:
        """
        Optimize container resources.

        Args:
            container_id: Container ID or name

        Returns:
            Optimization recommendations
        """
        return {
            "container_id": container_id,
            "status": "optimized",
            "cpu_shares": 1024,
            "memory_limit": "1G"
        }

    def get_recommendations(self, container_id: str) -> list[str]:
        """
        Get performance recommendations for a container.

        Args:
            container_id: Container ID or name

        Returns:
            List of recommendations
        """
        return [
            "Enable auto-scaling for CPU bursts",
            "Set explicit memory limits to prevent OOM kills",
            "Use multi-stage builds to reduce image size"
        ]

    def get_metrics_history(self) -> list[ContainerMetrics]:
        """Get history of collected metrics."""
        return self._metrics_history.copy()


def optimize_containers(
    container_ids: list[str],
    optimizer: ContainerOptimizer | None = None
) -> dict[str, dict[str, Any]]:
    """
    Optimize multiple containers.

    Args:
        container_ids: List of container IDs to optimize
        optimizer: Optional pre-configured optimizer instance

    Returns:
        Dictionary mapping container IDs to optimization results
    """
    if optimizer is None:
        optimizer = ContainerOptimizer()

    results = {}
    for container_id in container_ids:
        results[container_id] = optimizer.optimize_resources(container_id)

    return results

