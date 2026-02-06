# Agent Guidelines - Metrics

## Module Overview

Metrics collection, aggregation, and export to Prometheus/StatsD.

## Key Classes

- **Counter** — Monotonically increasing values
- **Gauge** — Values that can go up and down
- **Histogram** — Value distributions with buckets
- **Summary** — Quantile-based summaries
- **PrometheusExporter** — Expose /metrics endpoint
- **MetricAggregator** — Aggregate across sources

## Agent Instructions

1. **Use semantic names** — Name metrics like `http_requests_total`, not `counter1`
2. **Add labels sparingly** — Labels create new time series; use for method, status, path
3. **Choose metric type correctly** — Counter for totals, Gauge for current state, Histogram for latency
4. **Initialize at startup** — Define metrics once, not per-request
5. **Aggregate for dashboards** — Use `MetricAggregator` for consolidated views

## Integration Points

- **performance** — Use with `monitor_performance` decorator
- **logging_monitoring** — Correlate metrics with logs
- **api** — Instrument request handling

## Testing Patterns

```python
# Verify counter increments
counter = Counter("test_counter", "Test")
counter.inc()
counter.inc(5)
assert counter.value() == 6

# Verify histogram observations
histogram = Histogram("latency", "Request latency")
histogram.observe(0.1)
histogram.observe(0.2)
assert histogram.count() == 2
```

## Operating Contracts

- Maintain alignment between code, documentation, and workflows
- Ensure MCP interfaces remain available for sibling agents
- Record outcomes in shared telemetry

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
