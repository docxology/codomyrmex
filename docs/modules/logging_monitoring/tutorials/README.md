# Logging & Monitoring Tutorials

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Tutorials for configuring logging and monitoring in Codomyrmex.

## Available Tutorials

| Tutorial | Description |
|----------|-------------|
| [Basic Logging](#basic-logging) | Configure module logging |
| [Structured Logs](#structured-logs) | JSON structured logging |
| [Metrics](#metrics) | Collect and export metrics |

## Basic Logging

```python
from codomyrmex.logging_monitoring import get_logger

logger = get_logger("my_module")

logger.info("Processing started")
logger.debug("Debug details", extra={"item_id": 123})
logger.error("Operation failed", exc_info=True)
```

## Structured Logs

```python
from codomyrmex.logging_monitoring import configure_logging

# Enable JSON logging
configure_logging(
    format="json",
    level="INFO",
    output="stdout"
)

# Logs output as JSON
logger.info("Event", extra={"user_id": "123", "action": "login"})
```

## Metrics

```python
from codomyrmex.logging_monitoring import MetricsCollector

metrics = MetricsCollector()
metrics.increment("requests_total")
metrics.gauge("active_connections", 42)
metrics.histogram("request_duration", 0.125)
```

## Navigation

- **Parent**: [Logging Documentation](../README.md)
- **Source**: [src/codomyrmex/logging_monitoring/](../../../../src/codomyrmex/logging_monitoring/)
