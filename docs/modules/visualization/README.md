# Visualization Module Documentation

**Version**: v0.3.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Central visualization module that acts as the command center for the entire Codomyrmex ecosystem. Aggregates data visualizers from all specialized modules into a unified, interactive dashboard with HTML report generation, theming, and extensible plot and component libraries.

## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **Unified Dashboarding** -- Combines charts from different domains into a single view.
- **18+ Plot Types** -- Scatter, Heatmap, Bar, Line, Pie, Violin, Radar, Candlestick, Gantt, Sankey, and more.
- **UI Components** -- Card, Table, Badge, Alert, ProgressBar, Timeline, StatBox, ChatBubble, JsonView.
- **Domain Reports** -- GeneralSystemReport, FinanceReport, MarketingReport, LogisticsReport.
- **Theming** -- Centralized control over look-and-feel via `Theme`.

## Quick Start

```python
from codomyrmex.visualization import GeneralSystemReport, Dashboard, ScatterPlot, Card

# Generate a system report
report = GeneralSystemReport()
report.save("dashboard.html")

# Build a custom dashboard
dashboard = Dashboard("My Dashboard")
dashboard.add_section("Metric", Card(title="Users", value=1234))
dashboard.add_section("Growth", ScatterPlot("Growth", [1, 2, 3], [10, 20, 30]))
dashboard.render("custom.html")
```

## API Reference

### Core

| Class | Description |
|-------|-------------|
| `Dashboard` | Base dashboard class |
| `Grid` | Grid and section layout logic |
| `Theme` | Theme and CSS definitions |

### Plots

| Class | Description |
|-------|-------------|
| `ScatterPlot` | Scatter plots |
| `Heatmap` | Heatmaps |
| `BarPlot` | Bar charts |
| `LinePlot` | Line charts |
| `PieChart` | Pie charts |
| `MermaidDiagram` | Mermaid diagram support |
| `NetworkGraph` | Network graph visualization |

### Components

| Class | Description |
|-------|-------------|
| `Card` / `Table` | Basic UI components |
| `Badge` / `Alert` | Status indicators |
| `ProgressBar` | Progress display |
| `Timeline` | Timeline visualization |
| `StatBox` | Metric display box |

### Reports

| Class | Description |
|-------|-------------|
| `GeneralSystemReport` | Executive dashboard |
| `FinanceReport` | Financial reporting |
| `MarketingReport` | Marketing analytics |
| `LogisticsReport` | Logistics reporting |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k visualization -v
```

## Related Modules

- [Data Visualization](../data_visualization/README.md)

## Navigation

- **Source**: [src/codomyrmex/visualization/](../../../src/codomyrmex/visualization/)
- **API Spec**: [API_SPECIFICATION.md](../../../src/codomyrmex/visualization/API_SPECIFICATION.md)
- **MCP Spec**: [MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/visualization/MCP_TOOL_SPECIFICATION.md)
- **Parent**: [Modules](../README.md)
