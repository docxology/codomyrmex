# Data Visualization Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Comprehensive data visualization module providing chart generation, plotting engines, Mermaid diagram generation, and Git repository visualization. Supports multiple chart types (line, bar, scatter, histogram, pie, heatmap, box plot, area chart), configurable styles and color palettes, and an advanced plotting engine with dashboard creation. Includes specialized visualizers for Git branch topology and commit timelines.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

All exports below are available directly from `codomyrmex.data_visualization`:

| Export | Type | Description |
|--------|------|-------------|
| `Theme` | Class | Theme configuration for visual styling |
| `DEFAULT_THEME` | Instance | Pre-built light theme instance |
| `DARK_THEME` | Instance | Pre-built dark theme instance |
| `Dashboard` | Class | HTML dashboard container |
| `Card` | Class | Dashboard card component |
| `Table` | Class | Data table component |
| `Grid` | Class | Layout grid for dashboard sections |
| `Section` | Class | Named dashboard section |
| `render_html` | Function | Render component to HTML string |
| `generate_report` | Function | Generate and save typed HTML report |
| `Report` | Class | Base report class |
| `GeneralSystemReport` | Class | System overview report |
| `FinanceReport` | Class | Financial metrics report |
| `MarketingReport` | Class | Marketing analytics report |
| `LogisticsReport` | Class | Logistics operations report |
| `create_bar_chart` | Function | Create bar chart from data dict |
| `create_line_plot` | Function | Create line plot from data |
| `create_scatter_plot` | Function | Create scatter plot from data |
| `create_area_chart` | Function | Create area chart from data |
| `create_heatmap` | Function | Create heatmap from matrix data |
| `create_histogram` | Function | Create histogram from value list |
| `create_pie_chart` | Function | Create pie chart from category data |
| `create_box_plot` | Function | Create box plot from distribution data |
| `AreaChart` | Class | Area chart component |
| `BarChart` / `BarPlot` | Class | Bar chart component (BarPlot is alias) |
| `BoxPlot` | Class | Box plot component |
| `Heatmap` | Class | Heatmap component |
| `Histogram` | Class | Histogram component |
| `LinePlot` | Class | Line plot component |
| `PieChart` | Class | Pie chart component |
| `ScatterPlot` | Class | Scatter plot component |
| `MermaidDiagram` | Class | Mermaid diagram generator |

### Submodules

- **`charts/`** -- Individual chart type implementations (bar, line, scatter, histogram, pie, heatmap, box, area)
- **`themes/`** -- Chart theming and style configuration
- **`mermaid/`** -- Mermaid diagram generation for flowcharts, sequences, and Git diagrams
- **`engines/`** -- Advanced matplotlib-based plotting engine (see [Advanced API](#advanced-api) below)
- **`git/`** -- Git repository visualization

## Directory Contents

- `charts/` -- Chart type implementations: `line_plot.py`, `bar_chart.py`, `scatter_plot.py`, `histogram.py`, `pie_chart.py`, `heatmap.py`, `box_plot.py`, `area_chart.py`, `plot_utils.py`
- `engines/` -- Advanced plotting engine (`advanced_plotter.py`, `plotter.py`)
- `git/` -- Git repository visualization (`git_visualizer.py`)
- `mermaid/` -- Mermaid diagram generator (`mermaid_generator.py`)
- `themes/` -- Chart theme definitions and style configuration
- `exceptions.py` -- Visualization-specific exceptions

## Quick Start

```python
from codomyrmex.data_visualization import create_bar_chart, Dashboard, Theme, DEFAULT_THEME

# Create a simple bar chart
chart_html = create_bar_chart(
    {"categories": ["Q1", "Q2", "Q3", "Q4"], "values": [100, 150, 120, 180]},
    title="Quarterly Revenue"
)

# Build a dashboard
dashboard = Dashboard(title="My Dashboard", theme=DEFAULT_THEME)
dashboard.render(output_path="report.html")
```

```python
from codomyrmex.data_visualization import generate_report

# Generate a typed HTML report to disk
path = generate_report(output_dir="./reports", report_type="finance")
```

## Advanced API

For programmatic chart creation with matplotlib, use the `AdvancedPlotter` directly:

```python
from codomyrmex.data_visualization.engines.advanced_plotter import AdvancedPlotter
```

This provides `AdvancedPlotter`, `ChartStyle`, `ColorPalette`, `PlotType`, `PlotConfig`, `DataPoint`,
`Dataset`, `get_available_styles()`, and `create_dashboard()` for matplotlib-based workflows.
These are **not** re-exported from the top-level package and require the explicit submodule import
shown above.

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k data_visualization -v
```

## Consolidated Sub-modules

The following modules have been consolidated into this module as sub-packages:

| Sub-module | Description |
|------------|-------------|
| **`visualization/`** | Multi-format chart export and unified visualization |

Original standalone modules remain as backward-compatible re-export wrappers.

## Navigation

- **Full Documentation**: [docs/modules/data_visualization/](../../../docs/modules/data_visualization/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
