"""MCP tool definitions for the performance module.

Exposes regression detection and benchmark comparison as MCP tools.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs: Any):  # type: ignore[misc]
        """mcp Tool ."""
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func
        return decorator


@mcp_tool(
    category="performance",
    description="Check a benchmark result against a stored baseline for regressions.",
)
def performance_check_regression(
    benchmark_name: str,
    measured_value: float,
    baseline_mean: float,
    baseline_stddev: float = 0.0,
    warning_threshold: float = 0.10,
    critical_threshold: float = 0.25,
    higher_is_better: bool = False,
) -> dict[str, Any]:
    """Check a benchmark measurement for performance regression.

    Args:
        benchmark_name: Identifier for the benchmark.
        measured_value: The new measurement.
        baseline_mean: Historical mean value.
        baseline_stddev: Historical standard deviation.
        warning_threshold: Relative deviation for WARNING.
        critical_threshold: Relative deviation for CRITICAL.
        higher_is_better: If True, decrease = regression.
    """
    try:
        from codomyrmex.performance.analysis.regression_detector import (
            Baseline,
            BenchmarkResult,
            RegressionDetector,
        )
        detector = RegressionDetector()
        detector.set_baseline(Baseline(
            benchmark_name, mean=baseline_mean, stddev=baseline_stddev,
            warning_threshold=warning_threshold, critical_threshold=critical_threshold,
        ))
        result = BenchmarkResult(benchmark_name, value=measured_value, higher_is_better=higher_is_better)
        report = detector.check(result)
        return {
            "status": "ok",
            "benchmark": benchmark_name,
            "is_regression": report.is_regression,
            "severity": report.severity.value,
            "deviation": report.deviation,
            "message": report.message,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="performance",
    description="Compute the delta between two benchmark values.",
)
def performance_compare_benchmarks(
    name: str,
    before: float,
    after: float,
    higher_is_better: bool = False,
) -> dict[str, Any]:
    """Compare two benchmark measurements.

    Args:
        name: Benchmark identifier.
        before: Previous value.
        after: New value.
        higher_is_better: If True, increase = improvement.
    """
    try:
        from codomyrmex.performance.benchmarking.benchmark_comparison import (
            compute_delta,
        )
        delta = compute_delta(name, before, after, higher_is_better)
        return {
            "status": "ok",
            "name": name,
            "before": delta.before,
            "after": delta.after,
            "absolute_delta": delta.absolute_delta,
            "relative_delta_pct": delta.relative_delta,
            "improved": delta.improved,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
