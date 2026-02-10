# Metrics Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Metrics module for Codomyrmex.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **MetricsError** — Raised when metrics operations fail.
- `get_metrics()` — Get a metrics instance.

## Quick Start

```python
from codomyrmex.metrics import MetricsError

# Initialize
instance = MetricsError()
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |



## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k metrics -v
```

## Related Modules

- [Exceptions](../exceptions/README.md)

## Navigation

- **Source**: [src/codomyrmex/metrics/](../../../src/codomyrmex/metrics/)
- **Parent**: [Modules](../README.md)
