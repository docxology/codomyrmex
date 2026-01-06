# src/codomyrmex/metrics

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Overview

Metrics module providing metrics collection, aggregation, and Prometheus integration for the Codomyrmex platform. This module integrates with `performance` and `logging_monitoring` modules to provide comprehensive metrics tracking.

The metrics module serves as the metrics layer, providing backend-agnostic metrics interfaces with support for Prometheus and other metrics backends.

## Key Features

- **Multiple Backends**: Support for Prometheus, in-memory, and other metrics backends
- **Metric Types**: Counters, gauges, histograms, and summaries
- **Label Support**: Label-based metric organization
- **Export**: Export metrics to various backends
- **Aggregation**: Automatic metric aggregation and reporting

## Integration Points

- **performance/** - Performance metrics collection
- **logging_monitoring/** - Metrics logging integration
- **system_discovery/** - System metrics collection

## Usage Examples

```python
from codomyrmex.metrics import Metrics, Counter, Gauge

# Initialize metrics
metrics = Metrics(backend="prometheus")

# Create a counter
counter = metrics.counter("requests_total", labels={"method": "GET"})
counter.inc()

# Create a gauge
gauge = metrics.gauge("memory_usage", labels={"host": "server1"})
gauge.set(1024)

# Create a histogram
histogram = metrics.histogram("request_duration", labels={"endpoint": "/api"})
histogram.observe(0.5)

# Export metrics
exported = metrics.export()
```

## Navigation

- **Project Root**: [README](../../../README.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Related Modules**:
    - [performance](../performance/README.md) - Performance monitoring
    - [logging_monitoring](../logging_monitoring/README.md) - Logging system

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.metrics import Metrics, Counter, Gauge, Histogram

metrics = Metrics()
# Use metrics for collecting and exporting metrics
```

## Contributing

We welcome contributions! Please ensure you:
1. Follow the project coding standards.
2. Add tests for new functionality.
3. Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->

