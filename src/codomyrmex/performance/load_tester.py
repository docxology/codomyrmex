"""Load testing for concurrent agent sessions.

Simulates concurrent workloads and measures throughput,
latency, and error rates under load.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class LoadTestResult:
    """Result of a load test.

    Attributes:
        total_requests: Total requests executed.
        successful: Successful requests.
        failed: Failed requests.
        total_ms: Total test duration.
        mean_latency_ms: Mean request latency.
        p95_latency_ms: 95th percentile latency.
        throughput_per_sec: Requests per second.
        error_rate: Fraction of failed requests.
    """

    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    total_ms: float = 0.0
    mean_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    throughput_per_sec: float = 0.0
    error_rate: float = 0.0


class LoadTester:
    """Simulate concurrent load and measure performance.

    Example::

        tester = LoadTester()
        result = tester.run(
            fn=lambda: do_work(),
            total_requests=1000,
        )
        assert result.error_rate < 0.01
    """

    def run(
        self,
        fn: Callable[[], Any],
        total_requests: int = 100,
    ) -> LoadTestResult:
        """Run a load test (sequential simulation).

        Args:
            fn: Function to call for each request.
            total_requests: Number of requests to execute.

        Returns:
            LoadTestResult with stats.
        """
        latencies: list[float] = []
        successes = 0
        failures = 0

        start = time.monotonic()

        for _ in range(total_requests):
            req_start = time.monotonic()
            try:
                fn()
                successes += 1
            except Exception:
                failures += 1
            elapsed = (time.monotonic() - req_start) * 1000
            latencies.append(elapsed)

        total_ms = (time.monotonic() - start) * 1000
        latencies.sort()

        n = len(latencies)
        mean = sum(latencies) / n if n > 0 else 0
        p95 = latencies[int(n * 0.95)] if n >= 20 else (latencies[-1] if latencies else 0)
        throughput = (total_requests / total_ms * 1000) if total_ms > 0 else 0
        error_rate = failures / total_requests if total_requests > 0 else 0

        return LoadTestResult(
            total_requests=total_requests,
            successful=successes,
            failed=failures,
            total_ms=total_ms,
            mean_latency_ms=mean,
            p95_latency_ms=p95,
            throughput_per_sec=throughput,
            error_rate=error_rate,
        )


__all__ = ["LoadTestResult", "LoadTester"]
