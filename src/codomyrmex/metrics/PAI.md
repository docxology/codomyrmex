# Personal AI Infrastructure — Metrics Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Metrics module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.metrics import Metrics, Counter, Gauge, get_metrics
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Metrics` | Class | Metrics |
| `Counter` | Class | Counter |
| `Gauge` | Class | Gauge |
| `Histogram` | Class | Histogram |
| `Summary` | Class | Summary |
| `PrometheusExporter` | Class | Prometheusexporter |
| `StatsDClient` | Class | Statsdclient |
| `MetricAggregator` | Class | Metricaggregator |
| `get_metrics` | Function/Constant | Get metrics |

## PAI Algorithm Phase Mapping

| Phase | Metrics Contribution |
|-------|------------------------------|
| **OBSERVE** | Data gathering and state inspection |
| **LEARN** | Learning and knowledge capture |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
