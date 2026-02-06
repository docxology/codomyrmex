# Personal AI Infrastructure — Data Visualization Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Data Visualization module provides PAI integration for charts and graphs.

## PAI Capabilities

### Chart Generation

Create visualizations:

```python
from codomyrmex.data_visualization import Chart

chart = Chart(type="line")
chart.add_data(x=[1, 2, 3], y=[10, 20, 15])
chart.title = "Metrics Over Time"
chart.export("metrics.png")
```

### Dashboard Building

Build data dashboards:

```python
from codomyrmex.data_visualization import Dashboard

dashboard = Dashboard()
dashboard.add_chart("users", users_chart)
dashboard.add_chart("revenue", revenue_chart)
dashboard.render("dashboard.html")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `Chart` | Create charts |
| `Dashboard` | Multi-chart layouts |
| `Exporter` | Export to formats |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
