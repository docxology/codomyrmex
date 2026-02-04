# Observability Dashboard Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Unified monitoring dashboards for system observability. Provides a complete metrics collection, alerting, and dashboard management framework. The module includes a thread-safe metric collector supporting counter, gauge, histogram, and summary metric types with configurable retention. An alert manager evaluates metrics against user-defined rules and fires/resolves alerts with severity levels. Dashboards are composed of configurable panels (graph, stat, table, heatmap, gauge, log) that pull data from the metric collector.

## Key Features

- **Metric Collection**: Record and query metrics with labels, timestamps, and configurable retention windows
- **Multiple Metric Types**: Support for counter, gauge, histogram, and summary metric types
- **Alert Rules Engine**: Define alert conditions as callable rules that evaluate metric dictionaries and fire alerts automatically
- **Alert Lifecycle**: Alerts fire when conditions are met, auto-resolve when conditions clear, and support manual acknowledgment
- **Dashboard Management**: Create, retrieve, list, and delete dashboards with named panels and descriptions
- **Panel Types**: Six panel types for visualization: graph, stat, table, heatmap, gauge, and log
- **Time-Range Queries**: Query metrics and panel data over configurable time windows
- **Automatic Cleanup**: Remove old metrics beyond the retention period to manage memory
- **Thread-Safe**: All metric recording, alert checking, and dashboard operations are protected with locks

## Key Components

| Component | Description |
|-----------|-------------|
| `MetricCollector` | Thread-safe collector for recording and querying time-series metrics with label support and retention cleanup |
| `AlertManager` | Manages alert rules, evaluates metrics against conditions, fires/resolves alerts, and tracks alert history |
| `DashboardManager` | Creates and manages dashboards, retrieves panel data from the metric collector over time ranges |
| `Dashboard` | A complete dashboard entity containing panels, refresh interval, tags, and description |
| `Panel` | A dashboard panel with type, title, associated metrics, query, options, and grid position |
| `Alert` | An alert instance with severity, fire/resolve timestamps, duration tracking, and active state |
| `MetricValue` | A single metric data point with name, value, timestamp, labels, and metric type |
| `MetricType` | Enum of metric types: COUNTER, GAUGE, HISTOGRAM, SUMMARY |
| `AlertSeverity` | Enum of alert severity levels: INFO, WARNING, ERROR, CRITICAL |
| `PanelType` | Enum of panel types: GRAPH, STAT, TABLE, HEATMAP, GAUGE, LOG |

## Quick Start

```python
from codomyrmex.observability_dashboard import (
    MetricCollector, MetricType, AlertManager, AlertSeverity
)

# Collect metrics
collector = MetricCollector(retention_minutes=60)
collector.record("http_requests_total", 1, labels={"method": "GET"}, metric_type=MetricType.COUNTER)
collector.record("cpu_usage", 0.75)
collector.record("memory_usage", 0.62)

# Query metrics
latest_cpu = collector.get_latest("cpu_usage")
print(f"CPU: {latest_cpu.value}")  # CPU: 0.75

all_names = collector.list_metric_names()
print(all_names)  # ["http_requests_total", "cpu_usage", "memory_usage"]
```

```python
from codomyrmex.observability_dashboard import AlertManager, AlertSeverity

# Set up alert rules
alerts = AlertManager()
alerts.add_rule(
    name="high_cpu",
    condition=lambda m: m.get("cpu_usage", 0) > 0.9,
    message="CPU usage exceeded 90%",
    severity=AlertSeverity.CRITICAL,
)
alerts.add_rule(
    name="high_memory",
    condition=lambda m: m.get("memory_usage", 0) > 0.85,
    message="Memory usage exceeded 85%",
    severity=AlertSeverity.WARNING,
)

# Check metrics against rules
new_alerts = alerts.check({"cpu_usage": 0.95, "memory_usage": 0.70})
print(f"Fired: {[a.name for a in new_alerts]}")  # ["high_cpu"]

# Get active alerts
active = alerts.get_active_alerts()
```

```python
from codomyrmex.observability_dashboard import (
    DashboardManager, MetricCollector, Panel, PanelType
)

# Create a dashboard with panels
collector = MetricCollector()
dashboards = DashboardManager(collector)

dash = dashboards.create("System Overview", description="Main system metrics")
dash.add_panel(Panel(
    id="cpu_panel",
    title="CPU Usage",
    panel_type=PanelType.GRAPH,
    metrics=["cpu_usage"],
))
dash.add_panel(Panel(
    id="request_count",
    title="Request Count",
    panel_type=PanelType.STAT,
    metrics=["http_requests_total"],
))

# Retrieve panel data
data = dashboards.get_panel_data("system_overview", "cpu_panel", duration_minutes=30)
```

## Related Modules

- [logging_monitoring](../logging_monitoring/) - Centralized structured logging that feeds into observability
- [notification](../notification/) - Send alert notifications through multiple channels
- [model_registry](../model_registry/) - Track model performance metrics alongside system metrics

## Navigation

- **Source**: [src/codomyrmex/observability_dashboard/](../../../src/codomyrmex/observability_dashboard/)
- **Parent**: [docs/modules/](../README.md)
