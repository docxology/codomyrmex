# Agent Guidelines - Observability Dashboard

## Module Overview

Metrics collection, alerting, and dashboard visualization.

## Key Classes

- **MetricCollector** — Collect and store metrics with retention
- **AlertManager** — Define rules and fire alerts
- **DashboardManager** — Create and manage dashboards
- **Dashboard** — Dashboard with panels
- **Panel** — Visualization panel

## Agent Instructions

1. **Use semantic metric names** — Name like `http_requests_total` not `counter1`
2. **Add labels sparingly** — Labels create cardinality; use for dimensions
3. **Set appropriate retention** — Balance memory vs history needs
4. **Define alerts early** — Set up rules before collecting metrics
5. **Cleanup old data** — Call `collector.cleanup_old()` periodically

## Common Patterns

```python
from codomyrmex.observability_dashboard import (
    MetricCollector, AlertManager, DashboardManager, PanelType
)

# Set up observability stack
collector = MetricCollector(retention_minutes=60)
alerts = AlertManager()
dashboards = DashboardManager(collector)

# Record metrics
collector.record("api_latency_ms", 45.2, labels={"endpoint": "/users"})

# Alert on high latency
alerts.add_rule(
    name="slow_api",
    condition=lambda m: m.get("api_latency_ms", 0) > 100,
    message="API is slow"
)

# Create dashboard
dash = dashboards.create("API Metrics")
```

## Testing Patterns

```python
# Verify metric recording
collector = MetricCollector()
collector.record("test", 42.0)
assert collector.get_latest("test").value == 42.0

# Verify alert firing
alerts = AlertManager()
alerts.add_rule("high", lambda m: m.get("v", 0) > 10, "High")
new = alerts.check({"v": 15})
assert len(new) == 1
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
