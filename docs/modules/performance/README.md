# Performance Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Performance optimization utilities for Codomyrmex.

## Key Features

- **performance_context** — No-op context manager if dependencies missing.
- `monitor_performance()` — No-op decorator if dependencies missing.
- `get_system_metrics()` — get system metrics
- `decorator()` — decorator

## Quick Start

```python
from codomyrmex.performance import performance_context

# Initialize
instance = performance_context()
```


## Installation

```bash
uv pip install codomyrmex
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `performance_context` | No-op context manager if dependencies missing. |

### Functions

| Function | Description |
|----------|-------------|
| `monitor_performance()` | No-op decorator if dependencies missing. |
| `get_system_metrics()` | get system metrics |
| `decorator()` | decorator |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |



## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k performance -v
```

## Related Modules

- [Exceptions](../exceptions/README.md)

## Navigation

- **Source**: [src/codomyrmex/performance/](../../../src/codomyrmex/performance/)
- **Parent**: [Modules](../README.md)
