"""Health, readiness, and liveness endpoint models.

Provides structured health check aggregation across modules.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health of a single component.

    Attributes:
        name: Component name.
        status: Health status.
        latency_ms: Response latency in ms.
        message: Optional status message.
    """

    name: str
    status: HealthStatus = HealthStatus.HEALTHY
    latency_ms: float = 0.0
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "name": self.name,
            "status": self.status.value,
            "latency_ms": round(self.latency_ms, 2),
            "message": self.message,
        }


@dataclass
class HealthReport:
    """Aggregated health report.

    Attributes:
        status: Overall status (worst of components).
        components: Individual component health.
        uptime_seconds: Server uptime.
        timestamp: Report timestamp.
    """

    status: HealthStatus = HealthStatus.HEALTHY
    components: list[ComponentHealth] = field(default_factory=list)
    uptime_seconds: float = 0.0
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        """post Init ."""
        if not self.timestamp:
            self.timestamp = time.time()

    @property
    def is_healthy(self) -> bool:
        """is Healthy ."""
        return self.status == HealthStatus.HEALTHY

    @property
    def component_count(self) -> int:
        """component Count ."""
        return len(self.components)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "status": self.status.value,
            "is_healthy": self.is_healthy,
            "uptime_seconds": round(self.uptime_seconds, 1),
            "components": [c.to_dict() for c in self.components],
        }


class HealthChecker:
    """Aggregates health across components.

    Usage::

        checker = HealthChecker()
        checker.register("database", lambda: ComponentHealth("database"))
        checker.register("cache", lambda: ComponentHealth("cache"))
        report = checker.check()
    """

    def __init__(self) -> None:
        """Initialize this instance."""
        self._checks: dict[str, Any] = {}
        self._start_time = time.time()

    def register(self, name: str, check_fn: Any) -> None:
        """Register a health check function."""
        self._checks[name] = check_fn

    def check(self) -> HealthReport:
        """Run all health checks and aggregate.

        Returns:
            ``HealthReport`` with overall status.
        """
        components: list[ComponentHealth] = []
        overall = HealthStatus.HEALTHY

        for name, check_fn in self._checks.items():
            start = time.time()
            try:
                result = check_fn()
                if isinstance(result, ComponentHealth):
                    result.latency_ms = (time.time() - start) * 1000
                    components.append(result)
                    if result.status == HealthStatus.UNHEALTHY:
                        overall = HealthStatus.UNHEALTHY
                    elif result.status == HealthStatus.DEGRADED and overall != HealthStatus.UNHEALTHY:
                        overall = HealthStatus.DEGRADED
                else:
                    components.append(ComponentHealth(name=name, latency_ms=(time.time() - start) * 1000))
            except Exception as exc:
                components.append(ComponentHealth(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=str(exc),
                    latency_ms=(time.time() - start) * 1000,
                ))
                overall = HealthStatus.UNHEALTHY

        return HealthReport(
            status=overall,
            components=components,
            uptime_seconds=time.time() - self._start_time,
        )

    def liveness(self) -> dict[str, Any]:
        """Simple liveness probe (always returns ok)."""
        return {"status": "alive", "uptime": round(time.time() - self._start_time, 1)}

    def readiness(self) -> dict[str, Any]:
        """Readiness probe (checks all components)."""
        report = self.check()
        return {"ready": report.is_healthy, **report.to_dict()}


__all__ = ["ComponentHealth", "HealthChecker", "HealthReport", "HealthStatus"]
