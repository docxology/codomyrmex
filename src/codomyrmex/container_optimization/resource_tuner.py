import typing
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional
import time

import docker
from loguru import logger

@dataclass
class ResourceUsage:
    """Resource usage information for a container."""
    container_id: str
    cpu_percent: float
    memory_usage_bytes: int
    memory_limit_bytes: int
    memory_percent: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "container_id": self.container_id,
            "cpu_percent": self.cpu_percent,
            "memory_usage_mb": self.memory_usage_bytes / (1024 * 1024),
            "memory_limit_mb": self.memory_limit_bytes / (1024 * 1024),
            "memory_percent": self.memory_percent,
            "timestamp": self.timestamp
        }

class ResourceTuner:
    """
    Analyzes container resource usage and suggests optimal limits.
    """

    def __init__(self, client: Optional[docker.DockerClient] = None):
        """Initialize the resource tuner."""
        try:
            self.client = client or docker.from_env()
        except Exception as e:
            logger.warning(f"Could not connect to Docker: {e}")
            self.client = None

    def analyze_usage(self, container_id: str) -> ResourceUsage:
        """
        Get current resource usage for a container.
        """
        if not self.client:
            raise RuntimeError("Docker client not available")

        try:
            container = self.client.containers.get(container_id)
            stats = container.stats(stream=False)
            
            # CPU calculation
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_percent = 0.0
            if system_delta > 0 and cpu_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage'].get('percpu_usage', [1])) * 100.0

            # Memory calculation
            mem_usage = stats['memory_stats']['usage']
            mem_limit = stats['memory_stats']['limit']
            mem_percent = (mem_usage / mem_limit) * 100.0 if mem_limit > 0 else 0.0
            
            return ResourceUsage(
                container_id=container_id,
                cpu_percent=cpu_percent,
                memory_usage_bytes=mem_usage,
                memory_limit_bytes=mem_limit,
                memory_percent=mem_percent
            )
        except docker.errors.NotFound:
            raise ValueError(f"Container '{container_id}' not found")
        except Exception as e:
            logger.error(f"Failed to analyze container {container_id}: {e}")
            raise

    def suggest_limits(self, usage: ResourceUsage) -> Dict[str, str]:
        """
        Suggest optimal resource limits based on usage.
        """
        # Suggest 20% overhead for memory
        suggested_mem_mb = int((usage.memory_usage_bytes * 1.2) / (1024 * 1024))
        # Ensure at least 64MB
        suggested_mem_mb = max(64, suggested_mem_mb)
        
        # Suggest 0.5 CPU if usage < 10%, otherwise current + 0.5
        suggested_cpu = 0.5 if usage.cpu_percent < 10 else (usage.cpu_percent / 100.0) + 0.5
        
        return {
            "cpu_limit": f"{suggested_cpu:.1f}",
            "memory_limit": f"{suggested_mem_mb}m",
            "reasoning": f"Based on peak usage of {usage.cpu_percent:.1f}% CPU and {usage.memory_usage_bytes / (1024*1024):.1f}MB memory."
        }
