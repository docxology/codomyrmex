# Agent Guidelines - Data Visualization

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Charts, graphs, and visual data representations.

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

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
