"""
Deployment health check implementations.

Provides health check utilities for deployment monitoring.
"""

import asyncio
import json
import socket
import time
import urllib.request
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    name: str
    status: HealthStatus
    message: str = ""
    latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


@dataclass
class AggregatedHealth:
    """Aggregated health status from multiple checks."""
    overall_status: HealthStatus
    checks: list[HealthCheckResult]
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def healthy_count(self) -> int:
        """healthy Count ."""
        return sum(1 for c in self.checks if c.status == HealthStatus.HEALTHY)

    @property
    def unhealthy_count(self) -> int:
        """unhealthy Count ."""
        return sum(1 for c in self.checks if c.status == HealthStatus.UNHEALTHY)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "overall_status": self.overall_status.value,
            "healthy_count": self.healthy_count,
            "unhealthy_count": self.unhealthy_count,
            "total_checks": len(self.checks),
            "checks": [c.to_dict() for c in self.checks],
            "timestamp": self.timestamp.isoformat(),
        }


class HealthCheck(ABC):
    """Abstract base class for health checks."""

    def __init__(
        self,
        name: str,
        timeout: float = 5.0,
        critical: bool = True,
    ):
        """Initialize this instance."""
        self.name = name
        self.timeout = timeout
        self.critical = critical

    @abstractmethod
    def check(self) -> HealthCheckResult:
        """Perform the health check."""
        pass

    async def check_async(self) -> HealthCheckResult:
        """Perform the health check asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.check)


class HTTPHealthCheck(HealthCheck):
    """HTTP endpoint health check."""

    def __init__(
        self,
        name: str,
        url: str,
        method: str = "GET",
        expected_status: int = 200,
        expected_body: str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 5.0,
        critical: bool = True,
    ):
        """Initialize this instance."""
        super().__init__(name, timeout, critical)
        self.url = url
        self.method = method
        self.expected_status = expected_status
        self.expected_body = expected_body
        self.headers = headers or {}

    def check(self) -> HealthCheckResult:
        """Check the condition and return the result."""
        start_time = time.time()

        try:
            request = urllib.request.Request(
                self.url,
                method=self.method,
                headers=self.headers,
            )

            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                latency_ms = (time.time() - start_time) * 1000
                body = response.read().decode('utf-8')
                status_code = response.status

                if status_code != self.expected_status:
                    return HealthCheckResult(
                        name=self.name,
                        status=HealthStatus.UNHEALTHY,
                        message=f"Expected status {self.expected_status}, got {status_code}",
                        latency_ms=latency_ms,
                        details={"status_code": status_code},
                    )

                if self.expected_body and self.expected_body not in body:
                    return HealthCheckResult(
                        name=self.name,
                        status=HealthStatus.UNHEALTHY,
                        message="Response body mismatch",
                        latency_ms=latency_ms,
                    )

                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="OK",
                    latency_ms=latency_ms,
                    details={"status_code": status_code},
                )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
                latency_ms=latency_ms,
            )


class TCPHealthCheck(HealthCheck):
    """TCP port connectivity health check."""

    def __init__(
        self,
        name: str,
        host: str,
        port: int,
        timeout: float = 5.0,
        critical: bool = True,
    ):
        """Initialize this instance."""
        super().__init__(name, timeout, critical)
        self.host = host
        self.port = port

    def check(self) -> HealthCheckResult:
        """Check the condition and return the result."""
        start_time = time.time()

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.host, self.port))
            sock.close()

            latency_ms = (time.time() - start_time) * 1000

            if result == 0:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message=f"Port {self.port} is open",
                    latency_ms=latency_ms,
                    details={"host": self.host, "port": self.port},
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Port {self.port} is closed",
                    latency_ms=latency_ms,
                    details={"host": self.host, "port": self.port},
                )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
                latency_ms=latency_ms,
            )


class CommandHealthCheck(HealthCheck):
    """Command execution health check."""

    def __init__(
        self,
        name: str,
        command: list[str],
        expected_exit_code: int = 0,
        expected_output: str | None = None,
        timeout: float = 10.0,
        critical: bool = True,
    ):
        """Initialize this instance."""
        super().__init__(name, timeout, critical)
        self.command = command
        self.expected_exit_code = expected_exit_code
        self.expected_output = expected_output

    def check(self) -> HealthCheckResult:
        """Check the condition and return the result."""
        import subprocess

        start_time = time.time()

        try:
            result = subprocess.run(
                self.command,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            latency_ms = (time.time() - start_time) * 1000

            if result.returncode != self.expected_exit_code:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Exit code {result.returncode}, expected {self.expected_exit_code}",
                    latency_ms=latency_ms,
                    details={"stderr": result.stderr[:500]},
                )

            if self.expected_output and self.expected_output not in result.stdout:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message="Output mismatch",
                    latency_ms=latency_ms,
                )

            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="OK",
                latency_ms=latency_ms,
            )

        except subprocess.TimeoutExpired:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Command timed out",
                latency_ms=latency_ms,
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
                latency_ms=latency_ms,
            )


class MemoryHealthCheck(HealthCheck):
    """Memory usage health check."""

    def __init__(
        self,
        name: str = "memory",
        warning_threshold: float = 80.0,
        critical_threshold: float = 95.0,
        timeout: float = 5.0,
        critical: bool = True,
    ):
        """Initialize this instance."""
        super().__init__(name, timeout, critical)
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold

    def check(self) -> HealthCheckResult:
        """Check the condition and return the result."""
        start_time = time.time()

        try:
            import psutil
            memory = psutil.virtual_memory()
            percent = memory.percent
            latency_ms = (time.time() - start_time) * 1000

            details = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent_used": percent,
            }

            if percent >= self.critical_threshold:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Memory usage critical: {percent}%",
                    latency_ms=latency_ms,
                    details=details,
                )
            elif percent >= self.warning_threshold:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.DEGRADED,
                    message=f"Memory usage high: {percent}%",
                    latency_ms=latency_ms,
                    details=details,
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message=f"Memory usage: {percent}%",
                    latency_ms=latency_ms,
                    details=details,
                )

        except ImportError:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message="psutil not available",
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
            )


class DiskHealthCheck(HealthCheck):
    """Disk space health check."""

    def __init__(
        self,
        name: str = "disk",
        path: str = "/",
        warning_threshold: float = 80.0,
        critical_threshold: float = 95.0,
        timeout: float = 5.0,
        critical: bool = True,
    ):
        """Initialize this instance."""
        super().__init__(name, timeout, critical)
        self.path = path
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold

    def check(self) -> HealthCheckResult:
        """Check the condition and return the result."""
        start_time = time.time()

        try:
            import shutil
            usage = shutil.disk_usage(self.path)
            percent = (usage.used / usage.total) * 100
            latency_ms = (time.time() - start_time) * 1000

            details = {
                "path": self.path,
                "total_gb": round(usage.total / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "percent_used": round(percent, 2),
            }

            if percent >= self.critical_threshold:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Disk usage critical: {percent:.1f}%",
                    latency_ms=latency_ms,
                    details=details,
                )
            elif percent >= self.warning_threshold:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.DEGRADED,
                    message=f"Disk usage high: {percent:.1f}%",
                    latency_ms=latency_ms,
                    details=details,
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message=f"Disk usage: {percent:.1f}%",
                    latency_ms=latency_ms,
                    details=details,
                )

        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
            )


class HealthChecker:
    """Manages multiple health checks."""

    def __init__(self):
        """Initialize this instance."""
        self.checks: list[HealthCheck] = []

    def add_check(self, check: HealthCheck) -> 'HealthChecker':
        """Add a health check."""
        self.checks.append(check)
        return self

    def run_all(self) -> AggregatedHealth:
        """Run all health checks."""
        results = [check.check() for check in self.checks]
        overall = self._determine_overall_status(results)

        return AggregatedHealth(
            overall_status=overall,
            checks=results,
        )

    async def run_all_async(self) -> AggregatedHealth:
        """Run all health checks asynchronously."""
        tasks = [check.check_async() for check in self.checks]
        results = await asyncio.gather(*tasks)
        overall = self._determine_overall_status(results)

        return AggregatedHealth(
            overall_status=overall,
            checks=results,
        )

    def _determine_overall_status(
        self,
        results: list[HealthCheckResult]
    ) -> HealthStatus:
        """Determine overall status from results."""
        critical_unhealthy = any(
            r.status == HealthStatus.UNHEALTHY
            for r, check in zip(results, self.checks)
            if check.critical
        )

        if critical_unhealthy:
            return HealthStatus.UNHEALTHY

        any_unhealthy = any(r.status == HealthStatus.UNHEALTHY for r in results)
        any_degraded = any(r.status == HealthStatus.DEGRADED for r in results)

        if any_unhealthy or any_degraded:
            return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY


__all__ = [
    "HealthStatus",
    "HealthCheckResult",
    "AggregatedHealth",
    "HealthCheck",
    "HTTPHealthCheck",
    "TCPHealthCheck",
    "CommandHealthCheck",
    "MemoryHealthCheck",
    "DiskHealthCheck",
    "HealthChecker",
]
