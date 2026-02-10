# Physical Management Module Documentation

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Physical object management, simulation, and tracking with spatial awareness.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **AnalyticsMetric** — Types of analytics metrics.
- **StreamingMode** — Streaming modes for data processing.
- **DataPoint** — A single data point in a stream.
- **AnalyticsWindow** — Time window for analytics calculations.
- **DataStream** — Real-time data stream with analytics capabilities.
- **StreamingAnalytics** — Central streaming analytics manager.

## Quick Start

```python
from codomyrmex.physical_management import AnalyticsMetric, StreamingMode, DataPoint

instance = AnalyticsMetric()
```

## Source Files

- `analytics.py`
- `object_manager.py`
- `sensor_integration.py`
- `simulation_engine.py`

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k physical_management -v
```

## Navigation

- **Source**: [src/codomyrmex/physical_management/](../../../src/codomyrmex/physical_management/)
- **Parent**: [Modules](../README.md)
