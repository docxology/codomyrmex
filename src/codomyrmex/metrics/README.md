# Metrics Module

**Version**: v0.1.0 | **Status**: Active

Metrics collection with Prometheus and StatsD integration.


## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes
- **`MetricsError`** — Raised when metrics operations fail.

### Functions
- **`get_metrics()`** — Get a metrics instance.

## Quick Start

```python
from codomyrmex.metrics import Metrics, Counter, Gauge, Histogram, get_metrics

metrics = get_metrics()

# Counter: incrementing values
requests = Counter("http_requests_total", "Total HTTP requests")
requests.inc()
requests.inc(5)

# Gauge: current values
connections = Gauge("active_connections", "Current connections")
connections.set(10)
connections.inc()
connections.dec()

# Histogram: value distributions
latency = Histogram("request_latency_seconds", "Request latency")
latency.observe(0.123)

# With labels
requests.labels(method="GET", path="/api").inc()
```

## Prometheus Export

```python
from codomyrmex.metrics import PrometheusExporter

exporter = PrometheusExporter(port=9090)
exporter.start()  # Serves /metrics endpoint
```

## Exports

| Class | Description |
|-------|-------------|
| `Metrics` | Main metrics registry |
| `Counter` | Monotonically increasing counter |
| `Gauge` | Value that can go up and down |
| `Histogram` | Distribution of values |
| `Summary` | Quantile-based summary |
| `PrometheusExporter` | Prometheus /metrics endpoint |
| `StatsDClient` | StatsD metric client |
| `MetricAggregator` | Aggregate metrics across sources |
| `get_metrics(backend)` | Factory function |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k metrics -v
```


## Documentation

- [Module Documentation](../../../docs/modules/metrics/README.md)
- [Agent Guide](../../../docs/modules/metrics/AGENTS.md)
- [Specification](../../../docs/modules/metrics/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
