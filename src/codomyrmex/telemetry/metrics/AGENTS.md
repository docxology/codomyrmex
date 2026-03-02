# Telemetry Metrics - Agentic Context

**Module**: `codomyrmex.telemetry.metrics`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Key Components

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `MetricAggregator` | Local metrics collection: counters (with labels), gauges, histograms with bucket boundaries | `increment()`, `set_gauge()`, `observe()`, `get_snapshot()`, `counter_rate()`, `reset()` |
| `HistogramBucket` | Configurable bucket boundaries with observation counting and overflow bucket | `observe()`, `mean` property, `to_dict()` |
| `PrometheusExporter` | Wrapper for `prometheus_client` exposing metrics via HTTP server | `start()` on configurable port/addr |
| `create_counter()` | Factory for `prometheus_client.Counter` | Returns `Counter` |
| `create_gauge()` | Factory for `prometheus_client.Gauge` | Returns `Gauge` |
| `create_histogram()` | Factory for `prometheus_client.Histogram` with optional custom buckets | Returns `Histogram` |
| `StatsDClient` | Wrapper for `statsd.StatsClient` sending metrics to a StatsD collector | `incr()`, `gauge()`, `timing()`, `timer()` |

## Operating Contracts

- `MetricAggregator` is standalone (no external dependencies); `PrometheusExporter` requires `prometheus_client`; `StatsDClient` requires `statsd`.
- `MetricAggregator.increment()` supports optional labels as `dict[str, str]`; labeled counters are stored separately from total counters.
- `HistogramBucket` default boundaries: `[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]` plus overflow.
- `counter_rate()` computes per-second rate since the first increment using `time.time()`.
- `reset()` clears counters and histograms but preserves gauges; `reset_all()` clears everything.

## Integration Points

- **prometheus_client**: Optional; provides `Counter`, `Gauge`, `Histogram`, `start_http_server`.
- **statsd**: Optional; StatsD UDP client for external metric backends (Datadog, Graphite).
- **telemetry/alerting**: `AlertEvaluator` reads from `MetricAggregator.snapshot()` for rule evaluation.
- **telemetry/dashboard**: `MetricCollector` provides time-series storage alongside `MetricAggregator`'s point-in-time aggregation.

## Constraints

- `StatsDClient` host/port default to `STATSD_HOST`/`STATSD_PORT` env vars, falling back to `localhost:8125`.
- `PrometheusExporter.start()` is idempotent; the HTTP server is started at most once per instance.
- `MetricAggregator` is not thread-safe; use external locking for concurrent access.
