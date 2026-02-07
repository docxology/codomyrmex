# Metrics — Functional Specification

**Module**: `codomyrmex.metrics`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Metrics module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `MetricsError` | Class | Raised when metrics operations fail. |
| `get_metrics()` | Function | Get a metrics instance. |

### Source Files

- `aggregator.py`
- `metrics.py`
- `prometheus_exporter.py`
- `statsd_client.py`

## 3. Dependencies

See `src/codomyrmex/metrics/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.metrics import MetricsError
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k metrics -v
```
