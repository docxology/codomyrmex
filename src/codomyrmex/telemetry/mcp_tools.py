"""MCP tool definitions for the telemetry module.

Exposes metric aggregation, snapshot, and telemetry status as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_aggregator():
    """Lazy import of MetricAggregator."""
    from codomyrmex.telemetry.metric_aggregator import MetricAggregator

    return MetricAggregator()


@mcp_tool(
    category="telemetry",
    description="Record metrics (counters, gauges, histograms) and return a snapshot.",
)
def telemetry_record_metrics(
    counters: dict[str, float] | None = None,
    gauges: dict[str, float] | None = None,
    observations: dict[str, list[float]] | None = None,
) -> dict[str, Any]:
    """Record metrics and return a snapshot of all recorded values.

    Args:
        counters: Dict of counter_name -> increment_value.
        gauges: Dict of gauge_name -> value.
        observations: Dict of histogram_name -> list of observed values.

    Returns:
        dict with keys: status, counters, gauges, histograms, timestamp
    """
    try:
        agg = _get_aggregator()

        for name, value in (counters or {}).items():
            agg.increment(name, value)

        for name, value in (gauges or {}).items():
            agg.gauge(name, value)

        for name, values in (observations or {}).items():
            for v in values:
                agg.observe(name, v)

        snap = agg.snapshot()
        return {
            "status": "success",
            "counters": snap.counters,
            "gauges": snap.gauges,
            "histograms": snap.histograms,
            "timestamp": snap.timestamp,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="telemetry",
    description="Check telemetry subsystem availability (tracing, spans, exporters).",
)
def telemetry_status() -> dict[str, Any]:
    """Check which telemetry subsystems are available.

    Returns:
        dict with keys: status, trace_context, span_processor, otlp_exporter
    """
    try:
        from codomyrmex.telemetry import (
            HAS_OTLP_EXPORTER,
            HAS_SPAN_PROCESSOR,
            HAS_TRACE_CONTEXT,
        )

        return {
            "status": "success",
            "trace_context": HAS_TRACE_CONTEXT,
            "span_processor": HAS_SPAN_PROCESSOR,
            "otlp_exporter": HAS_OTLP_EXPORTER,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="telemetry",
    description="Compute histogram statistics (min, max, mean, percentiles) for a set of values.",
)
def telemetry_histogram_stats(
    name: str,
    values: list[float],
) -> dict[str, Any]:
    """Compute histogram statistics for a set of observations.

    Args:
        name: Name of the histogram.
        values: List of observed values.

    Returns:
        dict with keys: status, name, stats
    """
    try:
        agg = _get_aggregator()
        for v in values:
            agg.observe(name, v)
        stats = agg.histogram_stats(name)
        return {
            "status": "success",
            "name": name,
            "stats": stats,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
