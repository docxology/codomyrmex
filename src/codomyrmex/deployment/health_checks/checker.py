"""HealthChecker: orchestrates multiple health checks with async support."""

import asyncio

from .checks import HealthCheck
from .models import AggregatedHealth, HealthCheckResult, HealthStatus


class HealthChecker:
    """Manages and runs multiple health checks."""

    def __init__(self):
        self.checks: list[HealthCheck] = []

    def add_check(self, check: HealthCheck) -> "HealthChecker":
        """Add a health check. Returns self for chaining."""
        self.checks.append(check)
        return self

    def run_all(self) -> AggregatedHealth:
        """Run all checks synchronously."""
        results = [check.check() for check in self.checks]
        return AggregatedHealth(
            overall_status=self._determine_overall_status(results),
            checks=results,
        )

    async def run_all_async(self) -> AggregatedHealth:
        """Run all checks concurrently."""
        results = await asyncio.gather(*[check.check_async() for check in self.checks])
        return AggregatedHealth(
            overall_status=self._determine_overall_status(list(results)),
            checks=list(results),
        )

    def _determine_overall_status(self, results: list[HealthCheckResult]) -> HealthStatus:
        """Determine overall status: critical failures → UNHEALTHY, any issues → DEGRADED."""
        critical_unhealthy = any(
            r.status == HealthStatus.UNHEALTHY
            for r, check in zip(results, self.checks, strict=False)
            if check.critical
        )
        if critical_unhealthy:
            return HealthStatus.UNHEALTHY

        if any(r.status in (HealthStatus.UNHEALTHY, HealthStatus.DEGRADED) for r in results):
            return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY
