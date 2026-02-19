# Metrics

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Metrics collection and aggregation for telemetry. Provides thread-safe metric types (counter, gauge, histogram, summary) with label support, a centralized metrics registry, and a timing context manager, following the Prometheus metric model.

## Key Exports

### Enums

- **`MetricType`** -- Metric types: COUNTER, GAUGE, HISTOGRAM, SUMMARY, TIMER

### Data Structures

- **`MetricSample`** -- A single metric observation with value, timestamp, and labels
- **`MetricDescriptor`** -- Describes a metric's name, type, description, label keys, and unit

### Metric Types

- **`Metric`** -- Abstract base class with thread-safe locking and label support
- **`Counter`** -- Monotonically increasing counter with `inc()` and label-aware value storage
- **`Gauge`** -- Bidirectional gauge with `set()`, `inc()`, and `dec()` operations
- **`Histogram`** -- Distribution metric with configurable buckets (default: 0.005 to 10.0), tracking count, sum, min, max, and mean
- **`Summary`** -- Quantile metric with configurable quantiles (default: p50, p90, p95, p99)
- **`Timer`** -- Context manager that records elapsed time into a Histogram

### Registry

- **`MetricsRegistry`** -- Central registry for creating, storing, and collecting metrics; provides typed factory methods (`counter()`, `gauge()`, `histogram()`, `summary()`) and `collect()` to gather all current values

## Directory Contents

- `__init__.py` - All metric types and registry (331 lines)
- `py.typed` - PEP 561 type stub marker

## Usage

```python
from codomyrmex.telemetry.metrics import MetricsRegistry, Timer

registry = MetricsRegistry()

requests = registry.counter("http_requests_total", "Total HTTP requests")
latency = registry.histogram("http_request_duration", "Request latency in seconds")

requests.inc(labels={"method": "GET", "path": "/api"})

with Timer(latency):
    process_request()

for name, value in registry.collect():
    print(f"{name}: {value}")
```

## Navigation

- **Parent Module**: [telemetry](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
