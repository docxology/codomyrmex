# Codomyrmex Agents -- src/codomyrmex/data_visualization/charts

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Matplotlib-based chart generation providing both functional (`create_*`) and class-based (`BarChart`, `ScatterPlot`, etc.) interfaces for bar charts, line plots, pie charts, histograms, scatter plots, area charts, box plots, and heatmaps. Three of the functional creators (`create_bar_chart`, `create_line_plot`, `create_pie_chart`) are decorated with `@mcp_tool` for MCP auto-discovery.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `bar_chart.py` | `create_bar_chart()`, `BarChart` | Vertical and horizontal bar charts via `@mcp_tool` |
| `line_plot.py` | `create_line_plot()`, `LinePlot` | Single and multi-line plots via `@mcp_tool` |
| `pie_chart.py` | `create_pie_chart()`, `PieChart` | Pie charts with explode and autopct via `@mcp_tool` |
| `scatter_plot.py` | `create_scatter_plot()`, `ScatterPlot` | Scatter plots with configurable size, color, and alpha |
| `histogram.py` | `create_histogram()`, `Histogram` | Distribution histograms with configurable bins |
| `area_chart.py` | `create_area_chart()`, `AreaChart` | Single and stacked area charts |
| `box_plot.py` | `create_box_plot()`, `BoxPlot` | Box plots accepting lists, list-of-lists, or dicts |
| `heatmap.py` | `create_heatmap()`, `Heatmap` | 2D heatmaps with annotation and colorbar support |
| `plot_utils.py` | `save_plot()`, `apply_theme_to_axes()`, `get_color_palette()` | Shared utilities: logging, saving, theming, color palettes |

## Operating Contracts

- Every `create_*` function validates input lengths and returns `None` with a warning log on empty or mismatched data.
- `save_plot()` auto-creates parent directories and detects file format from the extension.
- Theme integration uses `apply_theme_to_axes()` which falls back silently if `data_visualization.themes` is unavailable.
- All chart functions accept `output_path`, `show_plot`, and `theme` keyword arguments.
- Errors are logged via `logging_monitoring` before returning.

## Integration Points

- **Depends on**: `matplotlib`, `numpy`, `logging_monitoring`, `model_context_protocol.decorators` (`@mcp_tool`), `data_visualization.themes` (optional)
- **Used by**: `data_visualization.engines.plotter` (re-exports all `create_*` functions), `data_visualization.engines.advanced_plotter`

## Navigation

- **Parent**: [data_visualization](../README.md)
- **Root**: [Root](../../../../README.md)
