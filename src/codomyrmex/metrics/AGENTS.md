# Codomyrmex Agents — src/codomyrmex/metrics

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Metrics Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Purpose

Metrics module providing metrics collection, aggregation, and Prometheus integration for the Codomyrmex platform. This module integrates with `performance` and `logging_monitoring` modules to provide comprehensive metrics tracking.

The metrics module serves as the metrics layer, providing backend-agnostic metrics interfaces with support for Prometheus and other metrics backends.

## Module Overview

### Key Capabilities
- **Counter Metrics**: Increment counters for event tracking
- **Gauge Metrics**: Set gauge values for current state
- **Histogram Metrics**: Record histogram values for distributions
- **Summary Metrics**: Record summary statistics
- **Export**: Export metrics to various backends

### Key Features
- Backend-agnostic metrics interface
- Support for Prometheus and other backends
- Label-based metric organization
- Automatic metric aggregation
- Export to multiple formats

## Function Signatures

### Metric Creation Functions

```python
def counter(name: str, labels: dict = None) -> Counter
```

Create a counter metric.

**Parameters:**
- `name` (str): Metric name
- `labels` (dict): Optional labels for metric organization

**Returns:** `Counter` - Counter metric object

```python
def gauge(name: str, labels: dict = None) -> Gauge
```

Create a gauge metric.

**Parameters:**
- `name` (str): Metric name
- `labels` (dict): Optional labels

**Returns:** `Gauge` - Gauge metric object

```python
def histogram(name: str, labels: dict = None) -> Histogram
```

Create a histogram metric.

**Parameters:**
- `name` (str): Metric name
- `labels` (dict): Optional labels

**Returns:** `Histogram` - Histogram metric object

```python
def summary(name: str, labels: dict = None) -> Summary
```

Create a summary metric.

**Parameters:**
- `name` (str): Metric name
- `labels` (dict): Optional labels

**Returns:** `Summary` - Summary metric object

### Metric Operations

```python
class Counter:
    def inc(value: float = 1.0) -> None
    def get() -> float
```

Counter metric operations.

```python
class Gauge:
    def set(value: float) -> None
    def inc(value: float = 1.0) -> None
    def dec(value: float = 1.0) -> None
    def get() -> float
```

Gauge metric operations.

```python
class Histogram:
    def observe(value: float) -> None
    def get() -> dict
```

Histogram metric operations.

### Export Functions

```python
def export() -> dict
```

Export all metrics to a dictionary format.

**Returns:** `dict` - Dictionary containing all metrics

```python
def export_prometheus() -> str
```

Export metrics in Prometheus format.

**Returns:** `str` - Prometheus-formatted metrics string

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `metrics.py` – Base metrics interface
- `backends/` – Backend implementations
  - `prometheus_backend.py` – Prometheus backend
  - `in_memory_backend.py` – In-memory backend

### Documentation
- `README.md` – Module usage and overview
- `AGENTS.md` – This file: agent documentation
- `SPEC.md` – Functional specification

## Operating Contracts

### Universal Metrics Protocols

All metrics operations within the Codomyrmex platform must:

1. **Label Consistency** - Use consistent label names across metrics
2. **Metric Naming** - Follow naming conventions for metrics
3. **Performance** - Minimize overhead of metric collection
4. **Export Format** - Support standard export formats
5. **Thread Safety** - Support concurrent metric updates

### Integration Guidelines

When integrating with other modules:

1. **Use Performance Module** - Integrate with performance monitoring
2. **Logging Integration** - Log metrics via logging_monitoring
3. **System Metrics** - Support system_discovery for system metrics
4. **Export Integration** - Support export to monitoring systems

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Related Modules**:
    - [performance](../performance/AGENTS.md) - Performance monitoring
    - [logging_monitoring](../logging_monitoring/AGENTS.md) - Logging system

