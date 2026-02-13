# Observability Dashboard Module

**Version**: v0.1.0 | **Status**: Active

Metrics collection, alerting, and dashboard visualization.


## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes
- **`MetricType`** — Types of metrics.
- **`AlertSeverity`** — Alert severity levels.
- **`PanelType`** — Dashboard panel types.
- **`MetricValue`** — A single metric value.
- **`Alert`** — An alert notification.
- **`Panel`** — A dashboard panel.
- **`Dashboard`** — A complete dashboard.
- **`MetricCollector`** — Collects and stores metrics.

## Quick Start

```python
from codomyrmex.observability_dashboard import (
    MetricCollector, AlertManager, DashboardManager,
    Dashboard, Panel, PanelType, AlertSeverity
)

# Collect metrics
collector = MetricCollector(retention_minutes=60)
collector.record("http_requests_total", 1, labels={"method": "GET"})
collector.record("cpu_usage", 0.75)

# Get latest values
latest = collector.get_latest("cpu_usage")
print(f"CPU: {latest.value}")

# Set up alerts
alerts = AlertManager()
alerts.add_rule(
    name="high_cpu",
    condition=lambda m: m.get("cpu_usage", 0) > 0.9,
    message="CPU usage is high",
    severity=AlertSeverity.WARNING
)

# Check metrics against rules
new_alerts = alerts.check({"cpu_usage": 0.95})

# Create dashboard
dashboards = DashboardManager(collector)
dash = dashboards.create("System Overview")
dash.add_panel(Panel(
    id="cpu",
    title="CPU Usage",
    panel_type=PanelType.GRAPH,
    metrics=["cpu_usage"]
))
```

## Exports

| Class | Description |
|-------|-------------|
| `MetricCollector` | Collect and store metrics |
| `AlertManager` | Define rules and fire alerts |
| `DashboardManager` | Create and manage dashboards |
| `Dashboard` | Dashboard with panels |
| `Panel` | Panel with type, metrics, position |
| `Alert` | Alert with severity, timestamps |
| `MetricValue` | Metric with value, labels, timestamp |
| `PanelType` | Enum: graph, stat, table, heatmap, gauge, log |
| `AlertSeverity` | Enum: info, warning, error, critical |


## Documentation

- [Module Documentation](../../../docs/modules/observability_dashboard/README.md)
- [Agent Guide](../../../docs/modules/observability_dashboard/AGENTS.md)
- [Specification](../../../docs/modules/observability_dashboard/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
