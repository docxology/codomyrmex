"""Canary deployment analysis.

Compares canary vs baseline metrics and determines
whether to promote or rollback.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class CanaryDecision(Enum):
    """Canary analysis outcome."""
    PROMOTE = "promote"
    ROLLBACK = "rollback"
    CONTINUE = "continue"


@dataclass
class MetricComparison:
    """Comparison of a single metric between canary and baseline.

    Attributes:
        metric_name: Name of the metric.
        baseline_value: Baseline measurement.
        canary_value: Canary measurement.
        threshold: Maximum acceptable deviation (percentage as decimal).
        passed: Whether canary is within threshold.
        message: Optional detail about the comparison.
    """

    metric_name: str
    baseline_value: float
    canary_value: float
    threshold: float = 0.1
    passed: bool = True
    message: str = ""

    def __post_init__(self) -> None:
        if self.baseline_value > 0:
            deviation = (self.canary_value - self.baseline_value) / self.baseline_value
            # For most metrics, lower is better (error rate, latency)
            # If deviation is positive and exceeds threshold, it's a failure
            if deviation > self.threshold:
                self.passed = False
                self.message = f"Exceeded threshold: +{deviation:.1%} (limit: {self.threshold:.1%})"
            else:
                self.passed = True
                self.message = f"Within threshold: {deviation:+.1%}"
        else:
            # Baseline is 0, so any value above threshold is a failure
            self.passed = self.canary_value <= self.threshold
            self.message = f"Value {self.canary_value} vs threshold {self.threshold}"

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "metric": self.metric_name,
            "baseline": round(self.baseline_value, 4),
            "canary": round(self.canary_value, 4),
            "threshold": self.threshold,
            "passed": self.passed,
            "message": self.message,
        }


@dataclass
class CanaryReport:
    """Result of canary analysis.

    Attributes:
        decision: Promote, rollback, or continue.
        comparisons: Individual metric comparisons.
        pass_rate: Fraction of metrics that passed.
    """

    decision: CanaryDecision = CanaryDecision.CONTINUE
    comparisons: list[MetricComparison] = field(default_factory=list)
    pass_rate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "decision": self.decision.value,
            "pass_rate": round(self.pass_rate, 3),
            "metrics": [c.to_dict() for c in self.comparisons],
            "total_metrics": len(self.comparisons),
        }


class CanaryAnalyzer:
    """Analyze canary deployment metrics.

    Usage::

        analyzer = CanaryAnalyzer(promote_threshold=0.9)
        report = analyzer.analyze(
            baseline={"error_rate": 0.01, "latency_p99": 200},
            canary={"error_rate": 0.015, "latency_p99": 210},
        )
        if report.decision == CanaryDecision.PROMOTE:
            print("Safe to promote!")
    """

    def __init__(
        self,
        promote_threshold: float = 0.9,
        rollback_threshold: float = 0.5,
        metric_tolerance: float = 0.1,
    ) -> None:
        self._promote_threshold = promote_threshold
        self._rollback_threshold = rollback_threshold
        self._metric_tolerance = metric_tolerance

    def analyze(
        self,
        baseline: dict[str, float],
        canary: dict[str, float],
        tolerances: dict[str, float] | None = None,
    ) -> CanaryReport:
        """Compare canary metrics against baseline.

        Args:
            baseline: Baseline metric values.
            canary: Canary metric values.
            tolerances: Per-metric tolerance overrides.

        Returns:
            ``CanaryReport`` with promotion decision.
        """
        tols = tolerances or {}
        comparisons: list[MetricComparison] = []

        all_metrics = set(baseline.keys()) | set(canary.keys())
        for name in sorted(all_metrics):
            base_val = baseline.get(name, 0.0)
            canary_val = canary.get(name, 0.0)
            tol = tols.get(name, self._metric_tolerance)
            comparisons.append(MetricComparison(
                metric_name=name,
                baseline_value=base_val,
                canary_value=canary_val,
                threshold=tol,
            ))

        passed_count = sum(1 for c in comparisons if c.passed)
        total_count = len(comparisons)
        pass_rate = passed_count / total_count if total_count > 0 else 1.0

        if pass_rate >= self._promote_threshold:
            decision = CanaryDecision.PROMOTE
        elif pass_rate < self._rollback_threshold:
            decision = CanaryDecision.ROLLBACK
        else:
            decision = CanaryDecision.CONTINUE

        report = CanaryReport(
            decision=decision,
            comparisons=comparisons,
            pass_rate=pass_rate,
        )

        logger.info(
            "Canary analysis completed: %s (Pass rate: %.1f%%)",
            decision.value, pass_rate * 100
        )

        return report


__all__ = ["CanaryAnalyzer", "CanaryDecision", "CanaryReport", "MetricComparison"]
