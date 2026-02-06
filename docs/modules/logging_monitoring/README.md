# Logging & Monitoring Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Centralized logging, metrics, and monitoring utilities.

## Key Features

- **Logging** — Structured logging
- **Metrics** — Prometheus metrics
- **Tracing** — Distributed tracing
- **Alerts** — Alerting rules

## Quick Start

```python
from codomyrmex.logging_monitoring import get_logger, MetricsCollector

logger = get_logger("my_module")
logger.info("Processing started", extra={"count": 42})

metrics = MetricsCollector()
metrics.increment("requests_total")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/logging_monitoring/](../../../src/codomyrmex/logging_monitoring/)
- **Parent**: [Modules](../README.md)
