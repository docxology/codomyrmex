# Codomyrmex Agents -- src/codomyrmex/data_visualization/engines

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Plotting engine layer providing two levels of abstraction over matplotlib/seaborn: `Plotter` (simple facade re-exporting chart functions) and `AdvancedPlotter` (stateful, multi-axis engine with style/palette/config management, performance monitoring, and dashboard creation).

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `plotter.py` | `Plotter` | Simple wrapper delegating to `charts.*` factory functions |
| `plotter.py` | `create_heatmap()` | Standalone heatmap function with `@monitor_performance` |
| `advanced_plotter.py` | `AdvancedPlotter` | Full-featured plotter with figure management, subplot support, and multiple chart methods |
| `advanced_plotter.py` | `PlotConfig` | Dataclass for figure size, DPI, style, palette, grid, legend settings |
| `advanced_plotter.py` | `PlotType`, `ChartStyle`, `ColorPalette` | Enums for 13 plot types, 7 chart styles, and 10 colour palettes |
| `advanced_plotter.py` | `DataPoint`, `Dataset` | Dataclasses for typed data input to `create_dashboard()` |
| `advanced_plotter.py` | `create_advanced_line_plot()`, etc. | Six convenience functions wrapping `AdvancedPlotter` |

## Operating Contracts

- `Plotter` is stateless: each method call creates and returns an independent figure.
- `AdvancedPlotter` is stateful: `create_figure()` sets `current_figure`/`current_axes`, subsequent `plot_*` calls draw onto those axes.
- All `AdvancedPlotter.plot_*` methods auto-create a figure if none exists.
- `finalize_plot()` applies title, labels, legend, grid, tight_layout, optional save, and optional show.
- `clear_figures()` closes all tracked figures to prevent memory leaks.
- `@monitor_performance` decorators are no-op when `codomyrmex.performance` is unavailable.

## Integration Points

- **Depends on**: `matplotlib`, `numpy`, `pandas`, `seaborn`, `data_visualization.charts.*`, `logging_monitoring`, `performance` (optional)
- **Used by**: MCP tool `generate_chart` and `export_dashboard`, any module needing programmatic chart generation

## Navigation

- **Parent**: [data_visualization](../README.md)
- **Root**: [Root](../../../../README.md)
