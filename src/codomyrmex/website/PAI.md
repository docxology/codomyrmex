# Personal AI Infrastructure — Website Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Website module provides PAI integration for generating web dashboards and static sites.

## PAI Capabilities

### Site Generation

Generate static websites:

```python
from codomyrmex.website import WebsiteGenerator

generator = WebsiteGenerator(output_dir="dist/")
generator.build([
    ("index.html", "home.j2", {"title": "Home"})
])
```

### Dashboard Building

Create data dashboards:

```python
from codomyrmex.website import DashboardBuilder

dashboard = DashboardBuilder()
dashboard.add_chart("metrics", chart_config)
dashboard.render("dashboard.html")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `WebsiteGenerator` | Static sites |
| `DashboardBuilder` | Data dashboards |
| `WebsiteServer` | Dev server |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
