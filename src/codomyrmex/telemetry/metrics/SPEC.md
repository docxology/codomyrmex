# Telemetry Metrics - Technical Specification

**Module**: `codomyrmex.telemetry.metrics`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Architecture

Three independent metric systems: `MetricAggregator` for local in-process collection, `PrometheusExporter` for HTTP-based Prometheus scraping, and `StatsDClient` for UDP push to StatsD collectors.

## Key Classes

### MetricAggregator

| Method | Signature | Description |
|--------|-----------|-------------|
| `increment` | `(name, value=1.0, labels?)` | Increment counter; optional label dimensions stored separately |
| `set_gauge` | `(name, value)` | Set gauge to absolute value |
| `observe` | `(name, value)` | Record histogram observation into configurable buckets |
| `get_snapshot` | `() -> dict` | Full snapshot: counters, gauges, histograms with timestamps |
| `counter_rate` | `(name) -> float` | Per-second rate since first increment |
| `reset` | `()` | Clear counters and histograms; gauges persist |
| `reset_all` | `()` | Clear everything including gauges |

### HistogramBucket

Configurable boundaries (default: `[0.005..10.0]` plus overflow). `observe(value)` increments the appropriate bucket. Properties: `mean`, `to_dict()` with `le_*` bucket counts.

### PrometheusExporter

| Method | Signature | Description |
|--------|-----------|-------------|
| `start` | `()` | Start `prometheus_client` HTTP server on `port` (default 8000) |

Factory functions: `create_counter()`, `create_gauge()`, `create_histogram()` returning `prometheus_client` metric objects.

### StatsDClient

| Method | Signature | Description |
|--------|-----------|-------------|
| `incr` | `(name, count=1, rate=1)` | Increment counter |
| `gauge` | `(name, value, rate=1)` | Set gauge |
| `timing` | `(name, dt, rate=1)` | Log timing in milliseconds |
| `timer` | `(name, rate=1)` | Context manager for timing a block |

Constructor: `StatsDClient(host?, port?, prefix="codomyrmex")`. Defaults from `STATSD_HOST`/`STATSD_PORT` env vars or `localhost:8125`.

## Dependencies

- `prometheus_client` (optional): Counter, Gauge, Histogram, start_http_server.
- `statsd` (optional): StatsClient for UDP metric push.
- No external deps for `MetricAggregator`.

## Constraints

- `MetricAggregator` is not thread-safe; callers must provide external synchronization for concurrent access.
- `HistogramBucket.counts` has `len(boundaries) + 1` slots; the last slot captures overflow values.
- `counter_rate()` uses wall-clock time since first increment; accuracy depends on monotonic increment patterns.
- `PrometheusExporter.start()` is idempotent; calling twice does not start a second server.
- Labeled counters in `MetricAggregator` are stored as comma-separated `k=v` strings in a nested defaultdict.

## Error Handling

- `StatsDClient` constructor raises if `statsd` package is not installed.
- `PrometheusExporter` constructor raises if `prometheus_client` package is not installed.
