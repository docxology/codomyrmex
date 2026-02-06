# Metrics Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Metrics collection, aggregation, and export for monitoring.

## Key Features

- **Counters** — Increment counters
- **Gauges** — Current values
- **Histograms** — Distribution tracking
- **Export** — Prometheus, StatsD

## Quick Start

```python
from codomyrmex.metrics import MetricsCollector

metrics = MetricsCollector()

metrics.increment("requests_total")
metrics.gauge("active_connections", 42)
metrics.histogram("request_duration", 0.125)
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/metrics/](../../../src/codomyrmex/metrics/)
- **Parent**: [Modules](../README.md)
