"""Container Performance Optimizer for Codomyrmex.

Provides container performance optimization and metrics:
- Container metrics collection
- Resource optimization
- Performance analysis
"""

import json
import shutil
import subprocess
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
        """Initialize the performance optimizer."""
        self._optimizations = {}

    def optimize(self, config: dict) -> dict:
        """Optimize container configuration.

        Raises NotImplementedError — no Docker CLI available to perform real optimization.
        Use ContainerOptimizer with Docker installed for real resource analysis.
        """
        raise NotImplementedError(
            "PerformanceOptimizer.optimize() requires Docker CLI to inspect running "
            "containers. Install Docker and use ContainerOptimizer.optimize_resources() instead."
        )


class ContainerOptimizer:
    """
    Container performance optimizer.

    Provides resource optimization for containers including:
    - CPU and memory allocation optimization
    - Resource limit recommendations
    - Performance tuning suggestions

    Requires Docker CLI to be installed for metric collection.
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
        Collect current metrics for a container via `docker stats`.

        Args:
            container_id: Container ID or name

        Returns:
            ContainerMetrics with current values from Docker

        Raises:
            NotImplementedError: If Docker CLI is not available
        """
        cli = shutil.which("docker")
        if not cli:
            raise NotImplementedError(
                "Docker CLI not available. Install Docker to collect real container metrics. "
                "See https://docs.docker.com/get-docker/"
            )
        try:
            result = subprocess.run(
                [
                    cli, "stats", "--no-stream",
                    "--format",
                    (
                        '{"id":"{{.ID}}","cpu":"{{.CPUPerc}}",'
                        '"mem_usage":"{{.MemUsage}}","mem_perc":"{{.MemPerc}}",'
                        '"net_io":"{{.NetIO}}","block_io":"{{.BlockIO}}"}'
                    ),
                    container_id,
                ],
                check=True, capture_output=True, text=True, timeout=15,
            )
            raw = json.loads(result.stdout.strip())

            def _parse_pct(s: str) -> float:
                return float(s.rstrip("%")) if s and s != "--" else 0.0

            def _parse_mb(s: str) -> float:
                """Parse strings like '128MiB / 1GiB' or '1.5GB' → MB."""
                if not s or s == "--":
                    return 0.0
                part = s.split("/")[0].strip()
                for unit, mult in [("GiB", 1024.0), ("MiB", 1.0), ("GB", 953.674),
                                   ("MB", 1.0), ("kB", 0.001), ("B", 0.000001)]:
                    if part.endswith(unit):
                        return float(part[: -len(unit)]) * mult
                return 0.0

            mem_parts = raw.get("mem_usage", "").split("/")
            mem_usage_mb = _parse_mb(mem_parts[0].strip()) if mem_parts else 0.0
            mem_limit_mb = _parse_mb(mem_parts[1].strip()) if len(mem_parts) > 1 else 0.0

            net_parts = raw.get("net_io", "").split("/")
            net_mb = _parse_mb(net_parts[0].strip()) if net_parts else 0.0

            blk_parts = raw.get("block_io", "").split("/")
            blk_mb = _parse_mb(blk_parts[0].strip()) if blk_parts else 0.0

            metrics = ContainerMetrics(
                container_id=container_id,
                cpu_percent=_parse_pct(raw.get("cpu", "0%")),
                memory_usage_mb=mem_usage_mb,
                memory_limit_mb=mem_limit_mb,
                network_io_mb=net_mb,
                disk_io_mb=blk_mb,
            )
            self._metrics_history.append(metrics)
            return metrics
        except subprocess.CalledProcessError as e:
            raise NotImplementedError(
                f"docker stats failed for container '{container_id}': {e.stderr.strip()}. "
                "Ensure the container is running and Docker has access."
            ) from e
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise NotImplementedError(
                f"Failed to parse docker stats output for '{container_id}': {e}"
            ) from e

    def optimize_resources(self, container_id: str) -> dict[str, Any]:
        """
        Produce data-driven resource optimization recommendations by inspecting
        the container via `docker inspect`.

        Args:
            container_id: Container ID or name

        Returns:
            Optimization recommendations based on current container configuration

        Raises:
            NotImplementedError: If Docker CLI is not available
        """
        cli = shutil.which("docker")
        if not cli:
            raise NotImplementedError(
                "Docker CLI not available. Install Docker to optimize container resources. "
                "See https://docs.docker.com/get-docker/"
            )
        try:
            result = subprocess.run(
                [cli, "inspect", "--format", "{{json .HostConfig}}", container_id],
                check=True, capture_output=True, text=True, timeout=10,
            )
            host_cfg = json.loads(result.stdout.strip())
            cpu_shares = host_cfg.get("CpuShares", 0)
            memory_bytes = host_cfg.get("Memory", 0)
            memory_mb = memory_bytes / (1024 * 1024) if memory_bytes else 0

            recommendations: dict[str, Any] = {"container_id": container_id, "status": "analyzed"}
            if cpu_shares == 0:
                recommendations["cpu_shares"] = 1024
                recommendations["cpu_note"] = "No CPU shares set; defaulting to 1024 (relative weight)"
            else:
                recommendations["cpu_shares"] = cpu_shares
            if memory_mb == 0:
                recommendations["memory_limit"] = "512m"
                recommendations["memory_note"] = "No memory limit set; recommend 512m minimum"
            else:
                recommendations["memory_limit"] = f"{int(memory_mb)}m"
            return recommendations
        except subprocess.CalledProcessError as e:
            raise NotImplementedError(
                f"docker inspect failed for '{container_id}': {e.stderr.strip()}"
            ) from e

    def get_recommendations(self, container_id: str) -> list[str]:
        """
        Get performance recommendations for a container based on current metrics.

        Collects real metrics and inspect data to produce container-specific advice.

        Args:
            container_id: Container ID or name

        Returns:
            List of specific, data-driven recommendations

        Raises:
            NotImplementedError: If Docker CLI is not available
        """
        metrics = self.collect_metrics(container_id)
        config = self.optimize_resources(container_id)

        recommendations: list[str] = []

        if metrics.cpu_percent > 80:
            recommendations.append(
                f"CPU usage is high ({metrics.cpu_percent:.1f}%). "
                "Consider increasing cpu_shares or adding CPU quotas."
            )
        if metrics.memory_percent > 85:
            recommendations.append(
                f"Memory usage is high ({metrics.memory_percent:.1f}% of limit). "
                "Consider increasing memory_limit or profiling for leaks."
            )
        if "memory_note" in config:
            recommendations.append(config["memory_note"])
        if "cpu_note" in config:
            recommendations.append(config["cpu_note"])
        if not recommendations:
            recommendations.append(
                f"Container '{container_id}' appears healthy "
                f"(CPU: {metrics.cpu_percent:.1f}%, Mem: {metrics.memory_percent:.1f}%)."
            )
        return recommendations

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
