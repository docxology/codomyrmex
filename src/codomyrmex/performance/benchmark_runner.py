"""Benchmark suite for performance certification.

Runs timed benchmarks on components, collects results,
and certifies performance against thresholds.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable


@dataclass
class BenchmarkResult:
    """Result of a single benchmark.

    Attributes:
        name: Benchmark name.
        iterations: Number of iterations.
        total_ms: Total elapsed time in ms.
        mean_ms: Mean time per iteration.
        min_ms: Fastest iteration.
        max_ms: Slowest iteration.
        ops_per_sec: Operations per second.
        passed: Whether it met the threshold.
        threshold_ms: Maximum allowed mean time.
    """

    name: str
    iterations: int = 0
    total_ms: float = 0.0
    mean_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0
    ops_per_sec: float = 0.0
    passed: bool = True
    threshold_ms: float = 0.0


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results.

    Attributes:
        name: Suite name.
        results: Individual benchmark results.
        total_ms: Total suite time.
        all_passed: Whether all benchmarks passed.
    """

    name: str = "Performance Suite"
    results: list[BenchmarkResult] = field(default_factory=list)
    total_ms: float = 0.0
    all_passed: bool = True


class BenchmarkRunner:
    """Run benchmarks and certify performance.

    Example::

        runner = BenchmarkRunner()
        runner.add("sort_1000", lambda: sorted(range(1000, 0, -1)), threshold_ms=1.0)
        suite = runner.run()
        assert suite.all_passed
    """

    def __init__(self, suite_name: str = "Performance Suite") -> None:
        """Execute   Init   operations natively."""
        self._suite_name = suite_name
        self._benchmarks: list[dict[str, Any]] = []

    @property
    def benchmark_count(self) -> int:
        """Execute Benchmark Count operations natively."""
        return len(self._benchmarks)

    def add(
        self,
        name: str,
        fn: Callable[[], Any],
        iterations: int = 100,
        threshold_ms: float = 0.0,
    ) -> None:
        """Register a benchmark.

        Args:
            name: Benchmark name.
            fn: Function to benchmark.
            iterations: Number of iterations.
            threshold_ms: Max allowable mean (0 = no limit).
        """
        self._benchmarks.append({
            "name": name,
            "fn": fn,
            "iterations": iterations,
            "threshold_ms": threshold_ms,
        })

    def run(self) -> BenchmarkSuite:
        """Execute all benchmarks.

        Returns:
            BenchmarkSuite with results.
        """
        suite_start = time.monotonic()
        results: list[BenchmarkResult] = []
        all_passed = True

        for bench in self._benchmarks:
            result = self._run_one(bench)
            results.append(result)
            if not result.passed:
                all_passed = False

        suite_total = (time.monotonic() - suite_start) * 1000

        return BenchmarkSuite(
            name=self._suite_name,
            results=results,
            total_ms=suite_total,
            all_passed=all_passed,
        )

    def _run_one(self, bench: dict[str, Any]) -> BenchmarkResult:
        """Execute  Run One operations natively."""
        fn = bench["fn"]
        iterations = bench["iterations"]
        threshold = bench["threshold_ms"]

        timings: list[float] = []
        for _ in range(iterations):
            start = time.monotonic()
            fn()
            elapsed = (time.monotonic() - start) * 1000
            timings.append(elapsed)

        total = sum(timings)
        mean = total / len(timings)
        passed = threshold <= 0 or mean <= threshold

        return BenchmarkResult(
            name=bench["name"],
            iterations=iterations,
            total_ms=total,
            mean_ms=mean,
            min_ms=min(timings),
            max_ms=max(timings),
            ops_per_sec=(1000 / mean) if mean > 0 else 0,
            passed=passed,
            threshold_ms=threshold,
        )

    def to_markdown(self, suite: BenchmarkSuite) -> str:
        """Render results as markdown."""
        lines = [
            f"# {suite.name}",
            "",
            f"**Total**: {suite.total_ms:.1f}ms | "
            f"**Passed**: {'✅' if suite.all_passed else '❌'}",
            "",
            "| Benchmark | Iterations | Mean (ms) | Ops/s | Status |",
            "|-----------|------------|-----------|-------|--------|",
        ]
        for r in suite.results:
            status = "✅" if r.passed else "❌"
            lines.append(
                f"| {r.name} | {r.iterations} | {r.mean_ms:.3f} | "
                f"{r.ops_per_sec:.0f} | {status} |"
            )
        return "\n".join(lines)


__all__ = ["BenchmarkResult", "BenchmarkRunner", "BenchmarkSuite"]
