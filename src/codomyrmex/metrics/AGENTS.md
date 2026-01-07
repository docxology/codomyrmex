# Codomyrmex Agents — src/codomyrmex/metrics

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Metrics collection, aggregation, and Prometheus integration. Provides backend-agnostic metrics interface with support for counters, gauges, histograms, and summaries.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `metrics.py` – Metrics collection and aggregation implementation

## Key Classes and Functions

### Metrics (`metrics.py`)
- `Metrics(backend: str = "in_memory")` – Initialize metrics with specified backend (in_memory, prometheus)
- `counter(name: str, labels: Optional[dict] = None) -> Counter` – Create or get a counter metric
- `gauge(name: str, labels: Optional[dict] = None) -> Gauge` – Create or get a gauge metric
- `histogram(name: str, labels: Optional[dict] = None) -> Histogram` – Create or get a histogram metric
- `summary(name: str, labels: Optional[dict] = None) -> Summary` – Create or get a summary metric
- `export() -> dict[str, Any]` – Export all metrics to a dictionary
- `export_prometheus() -> str` – Export metrics in Prometheus format

### Counter (`metrics.py`)
- `Counter` (dataclass) – Counter metric:
  - `name: str` – Metric name
  - `labels: dict[str, str]` – Metric labels
  - `value: float` – Counter value
- `inc(value: float = 1.0) -> None` – Increment counter
- `get() -> float` – Get counter value

### Gauge (`metrics.py`)
- `Gauge` (dataclass) – Gauge metric:
  - `name: str` – Metric name
  - `labels: dict[str, str]` – Metric labels
  - `value: float` – Gauge value
- `set(value: float) -> None` – Set gauge value
- `inc(value: float = 1.0) -> None` – Increment gauge
- `dec(value: float = 1.0) -> None` – Decrement gauge
- `get() -> float` – Get gauge value

### Histogram (`metrics.py`)
- `Histogram` (dataclass) – Histogram metric:
  - `name: str` – Metric name
  - `labels: dict[str, str]` – Metric labels
  - `values: list[float]` – Recorded values
- `observe(value: float) -> None` – Record a value
- `get() -> dict[str, Any]` – Get histogram statistics (count, sum, min, max, avg)

### Summary (`metrics.py`)
- `Summary` (dataclass) – Summary metric:
  - `name: str` – Metric name
  - `labels: dict[str, str]` – Metric labels
  - `count: int` – Number of observations
  - `sum: float` – Sum of values
- `observe(value: float) -> None` – Record a value
- `get() -> dict[str, Any]` – Get summary statistics (count, sum, avg)

### Module Functions (`__init__.py`)
- `get_metrics(backend: str = "in_memory") -> Metrics` – Get a metrics instance

### Exceptions
- `MetricsError` – Raised when metrics operations fail

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation