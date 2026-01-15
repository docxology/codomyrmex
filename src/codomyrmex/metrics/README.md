# Metrics Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Metrics module provides a comprehensive metrics collection and aggregation system for Codomyrmex. It implements standard metric types following Prometheus conventions and supports multiple export backends.

## Key Features

- **Counter**: Monotonically increasing values (e.g., request counts, errors)
- **Gauge**: Values that can go up or down (e.g., active connections, memory usage)
- **Histogram**: Distribution of values with statistical aggregation (min, max, avg, sum)
- **Summary**: Streaming aggregation of count and sum for efficient percentile calculation
- **Prometheus Export**: Native Prometheus-format metric export for monitoring integration
- **Label Support**: All metrics support labels for dimensional aggregation

## Quick Start

```python
from codomyrmex.metrics import Metrics

# Initialize metrics collector
metrics = Metrics(backend="in_memory")

# Create and use a counter
request_counter = metrics.counter("http_requests", labels={"endpoint": "/api/v1"})
request_counter.inc()

# Create and use a gauge
active_users = metrics.gauge("active_users")
active_users.set(42)
active_users.inc(5)

# Create and use a histogram
response_times = metrics.histogram("response_time_ms")
response_times.observe(123.5)
response_times.observe(98.2)
stats = response_times.get()  # {"count": 2, "sum": 221.7, "min": 98.2, ...}

# Export all metrics
all_metrics = metrics.export()

# Export in Prometheus format
prom_output = metrics.export_prometheus()
```

## Module Structure

| File | Description |
|------|-------------|
| `__init__.py` | Module exports and public API |
| `metrics.py` | Core metric types (Counter, Gauge, Histogram, Summary) and Metrics aggregator |
| `AGENTS.md` | Technical documentation for AI agents |
| `SPEC.md` | Functional specification |

## Metric Types

### Counter
- Monotonically increasing value
- Use for: request counts, error counts, bytes processed
- Methods: `inc(value=1.0)`, `get()`

### Gauge
- Value that can increase or decrease
- Use for: temperature, memory usage, active connections
- Methods: `set(value)`, `inc(value=1.0)`, `dec(value=1.0)`, `get()`

### Histogram
- Records observations and provides statistical aggregation
- Use for: request latencies, response sizes
- Methods: `observe(value)`, `get()` → returns count, sum, min, max, avg

### Summary
- Streaming aggregation of observations
- Use for: efficient count/sum tracking without storing all values
- Methods: `observe(value)`, `get()` → returns count, sum, avg

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
