"""Performance regression detection.

Compares benchmark results against stored baselines and flags
regressions when metrics exceed configured thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RegressionSeverity(Enum):
    """Severity level of a detected regression."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class BenchmarkResult:
    """A single benchmark measurement.

    Attributes:
        name: Benchmark identifier (e.g. "import_time").
        value: Measured value (lower is better by default).
        unit: Unit of measurement (e.g. "ms", "MB", "ops/s").
        higher_is_better: If True, value increase = improvement.
        metadata: Extra context (commit hash, env info, etc.).
    """

    name: str
    value: float
    unit: str = "ms"
    higher_is_better: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Baseline:
    """Stored baseline for a benchmark.

    Attributes:
        name: Benchmark identifier matching BenchmarkResult.name.
        mean: Mean value from historical runs.
        stddev: Standard deviation of historical runs.
        sample_count: Number of runs in baseline.
        warning_threshold: Relative deviation to trigger WARNING.
        critical_threshold: Relative deviation to trigger CRITICAL.
    """

    name: str
    mean: float
    stddev: float = 0.0
    sample_count: int = 1
    warning_threshold: float = 0.10   # 10% regression
    critical_threshold: float = 0.25  # 25% regression


@dataclass
class RegressionReport:
    """Report from comparing a benchmark result against its baseline.

    Attributes:
        benchmark_name: Name of the benchmark.
        baseline_mean: The baseline mean value.
        measured_value: The new measurement.
        deviation: Relative deviation from baseline (signed).
        severity: Assessed severity level.
        is_regression: Whether this constitutes a regression.
        message: Human-readable summary.
    """

    benchmark_name: str
    baseline_mean: float
    measured_value: float
    deviation: float
    severity: RegressionSeverity
    is_regression: bool
    message: str


class RegressionDetector:
    """Detect performance regressions by comparing against baselines.

    Example::

        detector = RegressionDetector()
        detector.set_baseline(Baseline("import_time", mean=120.0, stddev=5.0))
        result = BenchmarkResult("import_time", value=155.0, unit="ms")
        report = detector.check(result)
        if report.is_regression:
            print(report.message)
    """

    def __init__(self) -> None:
        self._baselines: dict[str, Baseline] = {}

    def set_baseline(self, baseline: Baseline) -> None:
        """Store or update a baseline for a benchmark."""
        self._baselines[baseline.name] = baseline

    def set_baselines(self, baselines: list[Baseline]) -> None:
        """Store multiple baselines at once."""
        for b in baselines:
            self._baselines[b.name] = b

    def get_baseline(self, name: str) -> Baseline | None:
        """Retrieve a stored baseline by name."""
        return self._baselines.get(name)

    @property
    def baseline_count(self) -> int:
        """Number of stored baselines."""
        return len(self._baselines)

    def check(self, result: BenchmarkResult) -> RegressionReport:
        """Check a benchmark result against its baseline.

        Args:
            result: The new benchmark measurement.

        Returns:
            A RegressionReport with deviation and severity.

        Raises:
            KeyError: If no baseline exists for the benchmark.
        """
        baseline = self._baselines.get(result.name)
        if baseline is None:
            raise KeyError(f"No baseline for benchmark '{result.name}'")

        if baseline.mean == 0:
            deviation = 0.0
        elif result.higher_is_better:
            # For higher-is-better metrics, decrease = regression
            deviation = (baseline.mean - result.value) / baseline.mean
        else:
            # For lower-is-better metrics, increase = regression
            deviation = (result.value - baseline.mean) / baseline.mean

        is_regression = deviation > 0
        if deviation >= baseline.critical_threshold:
            severity = RegressionSeverity.CRITICAL
        elif deviation >= baseline.warning_threshold:
            severity = RegressionSeverity.WARNING
        else:
            severity = RegressionSeverity.INFO
            is_regression = deviation > baseline.warning_threshold

        direction = "slower" if not result.higher_is_better else "lower"
        if deviation <= 0:
            direction = "faster" if not result.higher_is_better else "higher"

        message = (
            f"{result.name}: {result.value:.2f}{result.unit} "
            f"(baseline {baseline.mean:.2f}{result.unit}, "
            f"{abs(deviation)*100:.1f}% {direction}) "
            f"[{severity.value}]"
        )

        return RegressionReport(
            benchmark_name=result.name,
            baseline_mean=baseline.mean,
            measured_value=result.value,
            deviation=deviation,
            severity=severity,
            is_regression=is_regression,
            message=message,
        )

    def check_all(self, results: list[BenchmarkResult]) -> list[RegressionReport]:
        """Check multiple benchmark results against baselines.

        Results without a matching baseline are silently skipped.

        Args:
            results: List of benchmark measurements.

        Returns:
            List of RegressionReport objects.
        """
        reports = []
        for r in results:
            if r.name in self._baselines:
                reports.append(self.check(r))
        return reports

    def regressions_only(self, reports: list[RegressionReport]) -> list[RegressionReport]:
        """Filter reports to include only actual regressions."""
        return [r for r in reports if r.is_regression]

    def summary(self, reports: list[RegressionReport]) -> str:
        """Generate a text summary of regression reports.

        Args:
            reports: List of reports from check_all.

        Returns:
            Multi-line summary string.
        """
        regressions = self.regressions_only(reports)
        lines = [f"Performance Report: {len(reports)} benchmarks, {len(regressions)} regressions"]
        for r in reports:
            flag = "⚠" if r.is_regression else "✓"
            lines.append(f"  {flag} {r.message}")
        return "\n".join(lines)

    def clear(self) -> None:
        """Remove all stored baselines."""
        self._baselines.clear()
