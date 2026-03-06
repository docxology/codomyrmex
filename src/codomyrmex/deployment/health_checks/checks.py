"""Health check implementations: HTTP, TCP, Command, Memory, Disk."""

import asyncio
import socket
import time
from abc import ABC, abstractmethod
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .models import HealthCheckResult, HealthStatus

logger = get_logger(__name__)


class HealthCheck(ABC):
    """Abstract base class for health checks."""

    def __init__(self, name: str, timeout: float = 5.0, critical: bool = True):
        self.name = name
        self.timeout = timeout
        self.critical = critical

    @abstractmethod
    def check(self) -> HealthCheckResult:
        """Perform the health check."""

    async def check_async(self) -> HealthCheckResult:
        """Perform the health check asynchronously via executor."""
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
        super().__init__(name, timeout, critical)
        self.url = url
        self.method = method
        self.expected_status = expected_status
        self.expected_body = expected_body
        self.headers = headers or {}

    def check(self) -> HealthCheckResult:
        """Perform HTTP request and validate status/body."""
        import urllib.request

        start = time.time()
        try:
            req = urllib.request.Request(self.url, method=self.method, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                latency_ms = (time.time() - start) * 1000
                body = resp.read().decode("utf-8")
                code = resp.status

                if code != self.expected_status:
                    return HealthCheckResult(
                        self.name, HealthStatus.UNHEALTHY,
                        f"Expected status {self.expected_status}, got {code}",
                        latency_ms, details={"status_code": code},
                    )
                if self.expected_body and self.expected_body not in body:
                    return HealthCheckResult(
                        self.name, HealthStatus.UNHEALTHY, "Response body mismatch", latency_ms,
                    )
                return HealthCheckResult(
                    self.name, HealthStatus.HEALTHY, "OK", latency_ms,
                    details={"status_code": code},
                )
        except Exception as e:
            latency_ms = (time.time() - start) * 1000
            logger.debug("HTTP health check failed for %s: %s", self.url, e)
            return HealthCheckResult(self.name, HealthStatus.UNHEALTHY, str(e), latency_ms)


class TCPHealthCheck(HealthCheck):
    """TCP port connectivity health check."""

    def __init__(self, name: str, host: str, port: int, timeout: float = 5.0, critical: bool = True):
        super().__init__(name, timeout, critical)
        self.host = host
        self.port = port

    def check(self) -> HealthCheckResult:
        """Attempt TCP connection to host:port."""
        start = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            latency_ms = (time.time() - start) * 1000
            details: dict[str, Any] = {"host": self.host, "port": self.port}
            if result == 0:
                return HealthCheckResult(
                    self.name, HealthStatus.HEALTHY, f"Port {self.port} is open", latency_ms, details=details,
                )
            return HealthCheckResult(
                self.name, HealthStatus.UNHEALTHY, f"Port {self.port} is closed", latency_ms, details=details,
            )
        except Exception as e:
            latency_ms = (time.time() - start) * 1000
            return HealthCheckResult(self.name, HealthStatus.UNHEALTHY, str(e), latency_ms)


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
        super().__init__(name, timeout, critical)
        self.command = command
        self.expected_exit_code = expected_exit_code
        self.expected_output = expected_output

    def _validate_result(self, proc, latency_ms: float) -> HealthCheckResult:
        """Validate subprocess result against expected exit code and output."""
        if proc.returncode != self.expected_exit_code:
            return HealthCheckResult(
                self.name, HealthStatus.UNHEALTHY,
                f"Exit code {proc.returncode}, expected {self.expected_exit_code}",
                latency_ms, details={"stderr": proc.stderr[:500]},
            )
        if self.expected_output and self.expected_output not in proc.stdout:
            return HealthCheckResult(self.name, HealthStatus.UNHEALTHY, "Output mismatch", latency_ms)
        return HealthCheckResult(self.name, HealthStatus.HEALTHY, "OK", latency_ms)

    def check(self) -> HealthCheckResult:
        """Run command and check exit code and output."""
        import subprocess

        start = time.time()
        try:
            proc = subprocess.run(
                self.command, capture_output=True, text=True, timeout=self.timeout,
            )
            return self._validate_result(proc, (time.time() - start) * 1000)
        except subprocess.TimeoutExpired:
            return HealthCheckResult(
                self.name, HealthStatus.UNHEALTHY, "Command timed out",
                (time.time() - start) * 1000,
            )
        except Exception as e:
            return HealthCheckResult(
                self.name, HealthStatus.UNHEALTHY, str(e), (time.time() - start) * 1000,
            )


class MemoryHealthCheck(HealthCheck):
    """Memory usage health check (requires psutil)."""

    def __init__(
        self,
        name: str = "memory",
        warning_threshold: float = 80.0,
        critical_threshold: float = 95.0,
        timeout: float = 5.0,
        critical: bool = True,
    ):
        super().__init__(name, timeout, critical)
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold

    def _classify(self, percent: float, details: dict, latency_ms: float) -> HealthCheckResult:
        """Classify memory usage into HEALTHY / DEGRADED / UNHEALTHY."""
        if percent >= self.critical_threshold:
            return HealthCheckResult(self.name, HealthStatus.UNHEALTHY, f"Memory usage critical: {percent}%", latency_ms, details=details)
        if percent >= self.warning_threshold:
            return HealthCheckResult(self.name, HealthStatus.DEGRADED, f"Memory usage high: {percent}%", latency_ms, details=details)
        return HealthCheckResult(self.name, HealthStatus.HEALTHY, f"Memory usage: {percent}%", latency_ms, details=details)

    def check(self) -> HealthCheckResult:
        """Check system memory utilisation via psutil."""
        start = time.time()
        try:
            import psutil

            mem = psutil.virtual_memory()
            latency_ms = (time.time() - start) * 1000
            details = {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "percent_used": mem.percent,
            }
            return self._classify(mem.percent, details, latency_ms)
        except ImportError:
            return HealthCheckResult(self.name, HealthStatus.UNKNOWN, "psutil not available")
        except Exception as e:
            return HealthCheckResult(self.name, HealthStatus.UNHEALTHY, str(e))


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
        super().__init__(name, timeout, critical)
        self.path = path
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold

    def _classify(self, percent: float, details: dict, latency_ms: float) -> HealthCheckResult:
        """Classify disk usage into HEALTHY / DEGRADED / UNHEALTHY."""
        if percent >= self.critical_threshold:
            return HealthCheckResult(self.name, HealthStatus.UNHEALTHY, f"Disk usage critical: {percent:.1f}%", latency_ms, details=details)
        if percent >= self.warning_threshold:
            return HealthCheckResult(self.name, HealthStatus.DEGRADED, f"Disk usage high: {percent:.1f}%", latency_ms, details=details)
        return HealthCheckResult(self.name, HealthStatus.HEALTHY, f"Disk usage: {percent:.1f}%", latency_ms, details=details)

    def check(self) -> HealthCheckResult:
        """Check disk utilisation via shutil.disk_usage."""
        import shutil

        start = time.time()
        try:
            usage = shutil.disk_usage(self.path)
            percent = (usage.used / usage.total) * 100
            latency_ms = (time.time() - start) * 1000
            details = {
                "path": self.path,
                "total_gb": round(usage.total / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "percent_used": round(percent, 2),
            }
            return self._classify(percent, details, latency_ms)
        except Exception as e:
            return HealthCheckResult(self.name, HealthStatus.UNHEALTHY, str(e))
