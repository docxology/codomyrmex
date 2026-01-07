# metrics

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Metrics collection, aggregation, and Prometheus integration. Provides backend-agnostic metrics interface with support for counters, gauges, histograms, and summaries. Integrates with performance monitoring and logging systems.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `metrics.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.metrics import Metrics, get_metrics

# Get metrics instance
metrics = get_metrics(backend="in_memory")

# Counter metric
counter = metrics.counter("requests_total", labels={"method": "GET"})
counter.inc()

# Gauge metric
gauge = metrics.gauge("active_connections", labels={"service": "api"})
gauge.set(42)
gauge.inc(5)
gauge.dec(2)

# Histogram metric
histogram = metrics.histogram("request_duration", labels={"endpoint": "/api"})
histogram.observe(0.5)
histogram.observe(0.8)
stats = histogram.get()  # Returns count, sum, min, max, avg

# Summary metric
summary = metrics.summary("bytes_processed")
summary.observe(1024)
summary.observe(2048)

# Export metrics
all_metrics = metrics.export()  # Dictionary format
prometheus_format = metrics.export_prometheus()  # Prometheus format
```

