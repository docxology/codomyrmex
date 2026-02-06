# Personal AI Infrastructure — Metrics Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Metrics module provides PAI integration for tracking AI agent performance, usage, and system health.

## PAI Capabilities

### Agent Metrics

Track AI agent performance:

```python
from codomyrmex.metrics import MetricsCollector

metrics = MetricsCollector()
metrics.increment("llm_requests_total")
metrics.histogram("llm_latency_seconds", 0.125)
metrics.gauge("active_agents", 5)
```

### Usage Tracking

Monitor resource consumption:

```python
from codomyrmex.metrics import UsageTracker

tracker = UsageTracker()
tracker.record_tokens(prompt=100, completion=50)

print(f"Total tokens: {tracker.total_tokens}")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `MetricsCollector` | General metrics |
| `UsageTracker` | Token/cost tracking |
| `PerformanceMonitor` | Latency monitoring |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
