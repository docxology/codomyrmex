"""Benchmarking utilities with comparison, percentile, and reporting.

Provides:
- run_benchmark: multi-iteration function timing with stats
- profile_function: single-call time + memory profiling
- compare_benchmarks: side-by-side comparison of two functions
- BenchmarkSuite: named collection of benchmarks with tabular report
- PerformanceProfiler: class-based profiler for OO usage
"""

from __future__ import annotations

import logging
import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""

    name: str
    iterations: int
    times: list[float] = field(default_factory=list)

    @property
    def average_time(self) -> float:
        """average Time ."""
        return sum(self.times) / max(len(self.times), 1)

    @property
    def min_time(self) -> float:
        """min Time ."""
        return min(self.times) if self.times else 0.0

    @property
    def max_time(self) -> float:
        """max Time ."""
        return max(self.times) if self.times else 0.0

    @property
    def total_time(self) -> float:
        """total Time ."""
        return sum(self.times)

    @property
    def stdev(self) -> float:
        """stdev ."""
        return statistics.stdev(self.times) if len(self.times) > 1 else 0.0

    @property
    def median(self) -> float:
        """median ."""
        return statistics.median(self.times) if self.times else 0.0

    def percentile(self, p: float) -> float:
        """Compute the p-th percentile (0–100) of times."""
        if not self.times:
            return 0.0
        sorted_t = sorted(self.times)
        idx = (p / 100) * (len(sorted_t) - 1)
        lo = int(idx)
        hi = min(lo + 1, len(sorted_t) - 1)
        frac = idx - lo
        return sorted_t[lo] + frac * (sorted_t[hi] - sorted_t[lo])

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "name": self.name,
            "iterations": self.iterations,
            "average_time": self.average_time,
            "min_time": self.min_time,
            "max_time": self.max_time,
            "median": self.median,
            "stdev": self.stdev,
            "total_time": self.total_time,
            "p95": self.percentile(95),
            "p99": self.percentile(99),
        }


def run_benchmark(
    func: Callable[[], Any],
    iterations: int = 5,
    warmup: int = 0,
    name: str = "",
) -> dict[str, Any]:
    """Run a benchmark on a function.

    Args:
        func: Callable with no arguments (use lambda/partial for args).
        iterations: Number of measured iterations.
        warmup: Warmup iterations before measuring.
        name: Optional benchmark name.

    Returns:
        Dictionary containing benchmark statistics.
    """
    for _ in range(warmup):
        try:
            func()
        except Exception as e:
            logger.debug("Benchmark warmup iteration raised: %s", e)
            pass

    times: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        try:
            func()
        except Exception as e:
            logger.debug("Benchmark iteration raised: %s", e)
            pass
        times.append(time.perf_counter() - start)

    result = BenchmarkResult(name=name or "benchmark", iterations=len(times), times=times)
    return result.to_dict()


def profile_function(func: Callable, *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Profile a single function call for time and memory.

    Args:
        func: Function to profile.
        *args: Positional arguments.
        **kwargs: Keyword arguments.

    Returns:
        Dict with 'execution_time' (seconds) and 'memory_usage' (MB).
    """
    memory_before = 0.0
    if HAS_PSUTIL:
        process = psutil.Process()
        memory_before = process.memory_info().rss / (1024 * 1024)

    start = time.perf_counter()
    try:
        func(*args, **kwargs)
    except Exception as e:
        logger.debug("Profiled function raised: %s", e)
        pass
    execution_time = time.perf_counter() - start

    memory_after = 0.0
    if HAS_PSUTIL:
        memory_after = process.memory_info().rss / (1024 * 1024)

    return {
        "execution_time": execution_time,
        "memory_usage": max(0.0, memory_after - memory_before),
    }


def compare_benchmarks(
    func_a: Callable[[], Any],
    func_b: Callable[[], Any],
    iterations: int = 10,
    name_a: str = "A",
    name_b: str = "B",
) -> dict[str, Any]:
    """Compare two functions side-by-side.

    Returns:
        Dict with results for both functions and a speedup ratio.
    """
    result_a = run_benchmark(func_a, iterations=iterations, name=name_a)
    result_b = run_benchmark(func_b, iterations=iterations, name=name_b)
    avg_a = result_a["average_time"]
    avg_b = result_b["average_time"]
    speedup = avg_a / avg_b if avg_b > 0 else float("inf")
    return {
        name_a: result_a,
        name_b: result_b,
        "speedup": round(speedup, 3),
        "faster": name_b if speedup > 1.0 else name_a,
    }


class BenchmarkSuite:
    """Collection of named benchmarks with tabular reporting.

    Example::

        suite = BenchmarkSuite()
        suite.add("sort_1k", lambda: sorted(range(1000, 0, -1)))
        suite.add("sort_10k", lambda: sorted(range(10000, 0, -1)))
        suite.run_all()
        print(suite.report())
    """

    def __init__(self) -> None:
        """Initialize this instance."""
        self._benchmarks: dict[str, Callable[[], Any]] = {}
        self._results: dict[str, dict[str, Any]] = {}

    def add(self, name: str, func: Callable[[], Any]) -> None:
        """add ."""
        self._benchmarks[name] = func

    def run_all(self, iterations: int = 5, warmup: int = 1) -> dict[str, dict[str, Any]]:
        """Run all registered benchmarks."""
        self._results = {}
        for name, func in self._benchmarks.items():
            self._results[name] = run_benchmark(func, iterations=iterations, warmup=warmup, name=name)
        return dict(self._results)

    def report(self) -> str:
        """Generate a tabular report of results."""
        if not self._results:
            return "No benchmark results. Call run_all() first."
        lines = [f"{'Name':<20} {'Avg (ms)':>10} {'Min (ms)':>10} {'Max (ms)':>10} {'P95 (ms)':>10} {'StDev':>10}"]
        lines.append("-" * 70)
        for name, r in sorted(self._results.items()):
            lines.append(
                f"{name:<20} {r['average_time']*1000:>10.3f} {r['min_time']*1000:>10.3f} "
                f"{r['max_time']*1000:>10.3f} {r['p95']*1000:>10.3f} {r['stdev']*1000:>10.3f}"
            )
        return "\n".join(lines)

    @property
    def benchmark_count(self) -> int:
        """benchmark Count ."""
        return len(self._benchmarks)


class PerformanceProfiler:
    """Class-based profiler for consistency with tests."""

    def profile_function(self, func: Callable, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Profile a function."""
        return profile_function(func, *args, **kwargs)

    def benchmark(self, func: Callable[[], Any], iterations: int = 5) -> dict[str, Any]:
        """Run a benchmark."""
        return run_benchmark(func, iterations=iterations)
