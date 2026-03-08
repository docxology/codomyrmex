# Agent Guidelines - Data Visualization

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Charts, graphs, and visual data representations for the Codomyrmex platform. Provides `LineChart`
for time series, `BarChart` for categorical comparisons, `Dashboard` for multi-chart layouts, and
`VisualizationEngine` for rendering and theme control. Two MCP tools (`generate_chart`,
`export_dashboard`) expose chart generation and HTML export.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `Chart`, `LineChart`, `BarChart`, `Dashboard`, `VisualizationEngine`, `export_chart` |
| `charts.py` | `LineChart`, `BarChart` — core chart classes |
| `dashboard.py` | `Dashboard` — multi-chart layout manager |
| `visualization.py` | `VisualizationEngine`, `Theme` — rendering engine and theme control |
| `mcp_tools.py` | MCP tools: `generate_chart`, `export_dashboard` |

## Key Classes

- **Chart** — Base chart class
- **LineChart** — Time series visualization
- **BarChart** — Categorical comparisons
- **Dashboard** — Multiple chart layout
- **VisualizationEngine** — Core rendering and theme control

## Agent Instructions

1. **Choose chart type** — Match data to visualization
2. **Label clearly** — Axes, legends, titles
3. **Use color wisely** — Accessible palettes
4. **Interactive** — Add tooltips and zoom
5. **Export formats** — PNG, SVG, PDF support

## Common Patterns

```python
from codomyrmex.data_visualization import (
    LineChart, BarChart, Dashboard, export_chart
)

# Line chart for time series
chart = LineChart(title="User Growth")
chart.add_series("Users", dates, counts)
chart.set_axis("x", label="Date")
chart.set_axis("y", label="Active Users")

# Bar chart for comparisons
bar = BarChart(title="Module Usage")
bar.add_data(module_names, usage_counts)
bar.set_colors(["#3498db", "#2ecc71", "#e74c3c"])

# Dashboard with multiple charts
dashboard = Dashboard(title="Analytics")
dashboard.add_chart(chart, row=0, col=0)
dashboard.add_chart(bar, row=0, col=1)
dashboard.render("dashboard.html")

# Visualization Engine & Themes
from codomyrmex.data_visualization.visualization import VisualizationEngine, Theme
engine = VisualizationEngine(theme=Theme.DARK)
engine.render_to_file(data, "output.png")
```

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `generate_chart` | Generate a chart from data with specified type (line, bar, scatter) | SAFE |
| `export_dashboard` | Export a dashboard layout to HTML with embedded charts | SAFE |

## Operating Contracts

- `Dashboard.render()` requires all charts to be added before calling
- `VisualizationEngine.render_to_file()` creates the parent directory if it doesn't exist
- `generate_chart` MCP tool returns chart data as dict — not a file path; use `export_dashboard` for HTML export
- `export_chart()` is a convenience function — it wraps `VisualizationEngine.render_to_file()`
- **DO NOT** add more than 10 charts to a single Dashboard — performance degrades

## Testing Patterns

```python
# Verify chart creation
chart = LineChart()
chart.add_series("test", [1, 2], [10, 20])
assert len(chart.series) == 1

# Verify export
export_chart(chart, "/tmp/test.png")
assert Path("/tmp/test.png").exists()
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `generate_chart`, `export_dashboard` | TRUSTED |
| **Architect** | Read + Design | `generate_chart` — chart type selection, dashboard layout design | OBSERVED |
| **QATester** | Validation | `generate_chart`, `export_dashboard` — chart output validation, dashboard correctness | OBSERVED |
| **Researcher** | Read-only | `generate_chart`, `export_dashboard` — generate research visualizations | SAFE |

### Engineer Agent
**Use Cases**: Generating charts and dashboards during LEARN phase, visualizing metrics and test results, exporting dashboard HTML for reporting.

### Architect Agent
**Use Cases**: Designing visualization schemas, selecting appropriate chart types, planning dashboard layouts.

### QATester Agent
**Use Cases**: Validating chart output during VERIFY, confirming dashboard renders correctly, checking data accuracy.

### Researcher Agent
**Use Cases**: Generating charts and dashboards for research analysis and visual data presentation.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/data_visualization.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/data_visualization.cursorrules)
