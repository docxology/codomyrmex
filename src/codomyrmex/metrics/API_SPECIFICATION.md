# Metrics Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: January 2026

## 1. Overview
The `metrics` module provides observability primitives for Codomyrmex applications. It supports standard metric types (Counter, Gauge, Histogram, Summary) and pluggable backends (InMemory, Prometheus).

## 2. Core Components

### 2.1 Main Interface
- **`get_metrics(backend: str = "in_memory") -> Metrics`**: Factory function to obtain the global metrics registry.

### 2.2 Classes
- **`Metrics`**: The central registry.
- **`Counter`**: A cumulative metric that monotonically increases.
- **`Gauge`**: A metric that can go up and down.
- **`Histogram`**: Samples observations (usually things like request durations or response sizes) and counts them in configurable buckets.
- **`Summary`**: Similar to histograms but calculates quantiles on the client side.

## 3. Exceptions
- **`MetricsError`**: Base exception for metric collection or reporting failures.

## 4. Usage Example

```python
from codomyrmex.metrics import get_metrics

metrics = get_metrics()

# Create a counter
requests_total = metrics.create_counter(
    name="requests_total",
    description="Total number of requests",
    labels=["method", "endpoint"]
)

# Increment
requests_total.inc(labels={"method": "GET", "endpoint": "/api/v1/status"})
```
