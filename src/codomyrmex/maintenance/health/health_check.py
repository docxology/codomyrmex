"""Health check framework for maintenance tasks.

Provides a registry of health checks with configurable thresholds,
aggregated status reporting, and diagnostic output.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class HealthStatus(Enum):
    """Status of a health check."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of running a single health check.

    Attributes:
        name: Check identifier.
        status: Overall status.
        message: Human-readable status message.
        duration_ms: Time to run the check in milliseconds.
        details: Additional diagnostic data.
        timestamp: When the check was run.
    """

    name: str
    status: HealthStatus
    message: str = ""
    duration_ms: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class HealthCheck:
    """A registered health check.

    Attributes:
        name: Unique identifier for the check.
        description: What this check verifies.
        check_fn: Callable that returns (status, message, details).
        critical: If True, failure makes overall status UNHEALTHY.
        timeout_ms: Maximum execution time before auto-fail.
    """

    name: str
    description: str
    check_fn: Callable[[], tuple[HealthStatus, str, dict[str, Any]]]
    critical: bool = False
    timeout_ms: float = 5000.0


@dataclass
class AggregateHealthReport:
    """Aggregated health status across all checks.

    Attributes:
        overall_status: Worst status among all checks.
        checks: Individual check results.
        total_duration_ms: Total time to run all checks.
        healthy_count: Number of healthy checks.
        degraded_count: Number of degraded checks.
        unhealthy_count: Number of unhealthy checks.
    """

    overall_status: HealthStatus
    checks: list[HealthCheckResult] = field(default_factory=list)
    total_duration_ms: float = 0.0
    healthy_count: int = 0
    degraded_count: int = 0
    unhealthy_count: int = 0


class HealthChecker:
    """Manages and executes health checks.

    Supports registering multiple checks, running them individually
    or as a batch, and aggregating results into an overall report.

    Example::

        checker = HealthChecker()
        checker.register(HealthCheck(
            name="db_connection",
            description="Database connectivity",
            check_fn=lambda: (HealthStatus.HEALTHY, "Connected", {}),
            critical=True,
        ))
        report = checker.run_all()
    """

    def __init__(self) -> None:
        self._checks: dict[str, HealthCheck] = {}
        self._last_results: dict[str, HealthCheckResult] = {}

    def register(self, check: HealthCheck) -> None:
        """Register a health check."""
        self._checks[check.name] = check

    def unregister(self, name: str) -> bool:
        """Remove a health check. Returns True if found."""
        return self._checks.pop(name, None) is not None

    @property
    def check_count(self) -> int:
        """Number of registered checks."""
        return len(self._checks)

    def run(self, name: str) -> HealthCheckResult:
        """Run a single health check by name.

        Args:
            name: Check identifier.

        Returns:
            HealthCheckResult with status and diagnostics.

        Raises:
            KeyError: If no check with that name is registered.
        """
        check = self._checks.get(name)
        if check is None:
            raise KeyError(f"No health check registered: '{name}'")

        start = time.monotonic()
        try:
            status, message, details = check.check_fn()
            elapsed = (time.monotonic() - start) * 1000

            result = HealthCheckResult(
                name=name,
                status=status,
                message=message,
                duration_ms=elapsed,
                details=details,
            )
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            result = HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check raised exception: {exc}",
                duration_ms=elapsed,
                details={"error": str(exc)},
            )

        self._last_results[name] = result
        return result

    def run_all(self) -> AggregateHealthReport:
        """Run all registered health checks.

        Returns:
            AggregateHealthReport with individual results and aggregate status.
        """
        results = []
        for name in sorted(self._checks.keys()):
            results.append(self.run(name))

        healthy = sum(1 for r in results if r.status == HealthStatus.HEALTHY)
        degraded = sum(1 for r in results if r.status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for r in results if r.status == HealthStatus.UNHEALTHY)
        total_ms = sum(r.duration_ms for r in results)

        # Determine overall status
        if unhealthy > 0:
            overall = HealthStatus.UNHEALTHY
        elif degraded > 0:
            overall = HealthStatus.DEGRADED
        elif healthy > 0:
            overall = HealthStatus.HEALTHY
        else:
            overall = HealthStatus.UNKNOWN

        return AggregateHealthReport(
            overall_status=overall,
            checks=results,
            total_duration_ms=total_ms,
            healthy_count=healthy,
            degraded_count=degraded,
            unhealthy_count=unhealthy,
        )

    def last_result(self, name: str) -> HealthCheckResult | None:
        """Return the most recent result for a check."""
        return self._last_results.get(name)

    def summary_text(self, report: AggregateHealthReport) -> str:
        """Generate a text summary of a health report.

        Args:
            report: The aggregate report.

        Returns:
            Multi-line text summary.
        """
        lines = [
            f"Health: {report.overall_status.value.upper()} "
            f"({report.healthy_count}✓ {report.degraded_count}~ {report.unhealthy_count}✗)"
        ]
        for r in report.checks:
            icon = {"healthy": "✓", "degraded": "~", "unhealthy": "✗"}.get(r.status.value, "?")
            lines.append(f"  {icon} {r.name}: {r.message} ({r.duration_ms:.1f}ms)")
        return "\n".join(lines)

    def clear(self) -> None:
        """Remove all registered checks and cached results."""
        self._checks.clear()
        self._last_results.clear()
