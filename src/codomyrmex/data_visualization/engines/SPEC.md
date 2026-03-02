# Engines -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Two plotting engines with increasing capability: `Plotter` (thin facade over `charts.*` functions) and `AdvancedPlotter` (stateful, seaborn-powered engine with subplot management, styled palettes, and dashboard generation).

## Architecture

```
Plotter (plotter.py)
  └── Delegates to charts.create_bar_chart, create_line_plot, etc.

AdvancedPlotter (advanced_plotter.py)
  ├── PlotConfig (figsize, dpi, style, palette, grid, legend, save settings)
  ├── Manages current_figure / current_axes state
  ├── plot_line, plot_scatter, plot_bar, plot_histogram, plot_heatmap, plot_box, plot_violin, plot_correlation
  ├── create_dashboard (multi-panel from Dataset list)
  └── finalize_plot, save_plot, clear_figures
```

## Key Classes

### `Plotter`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `bar_chart` | `categories, values, **kwargs` | `Figure` | Delegates to `create_bar_chart` |
| `line_plot` | `x_data, y_data, **kwargs` | `Figure` | Delegates to `create_line_plot` |
| `scatter_plot` | `x_data, y_data, **kwargs` | `Figure` | Delegates to `create_scatter_plot` |
| `histogram` | `data, **kwargs` | `Figure` | Delegates to `create_histogram` |
| `pie_chart` | `labels, sizes, **kwargs` | `Figure` | Delegates to `create_pie_chart` |
| `heatmap` | `data, **kwargs` | `Figure` | Delegates to local `create_heatmap` |

### `AdvancedPlotter`

| Method | Key Parameters | Returns | Description |
|--------|---------------|---------|-------------|
| `create_figure` | `subplots=(1,1), **kwargs` | `(Figure, Axes)` | Create and track a new figure |
| `plot_line` | `x_data, y_data, label, color, linewidth, linestyle, marker` | `Line2D` | Line plot on current axes |
| `plot_scatter` | `x_data, y_data, label, color, size, alpha, marker` | `PathCollection` | Scatter plot |
| `plot_bar` | `x_data, y_data, orientation="vertical"` | `BarContainer` | Vertical or horizontal bar chart |
| `plot_histogram` | `data, bins, density, cumulative` | `(counts, edges, patches)` | Histogram |
| `plot_heatmap` | `data, x_labels, y_labels, cmap, annot` | `AxesImage` | Seaborn heatmap |
| `plot_box` | `data, labels, notch, patch_artist` | `dict` | Box plot |
| `plot_violin` | `data, labels, color, alpha` | violin elements | Seaborn violin plot |
| `plot_correlation` | `data (DataFrame), method, cmap` | `AxesImage` | Correlation heatmap |
| `create_dashboard` | `datasets: list[Dataset], layout=(2,2)` | `Figure` | Multi-panel dashboard |
| `finalize_plot` | `title, xlabel, ylabel, legend, grid, save_path` | `Figure` | Apply labels, legend, layout, save |
| `save_plot` | `path, format, dpi, transparent` | `bool` | Save current figure |
| `clear_figures` | -- | `None` | Close all tracked figures |

### `PlotConfig`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `figsize` | `tuple[int, int]` | `(10, 6)` | Figure dimensions |
| `dpi` | `int` | `100` | Display resolution |
| `style` | `ChartStyle` | `DEFAULT` | Seaborn style preset |
| `palette` | `ColorPalette` | `DEFAULT` | Colour palette |
| `save_dpi` | `int` | `300` | Save resolution |
| `save_format` | `str` | `"png"` | Default save format |

## Dependencies

- **Internal**: `data_visualization.charts.*`, `logging_monitoring`, `performance` (optional)
- **External**: `matplotlib`, `numpy`, `pandas`, `seaborn`

## Constraints

- `AdvancedPlotter` uses seaborn for `heatmap`, `violinplot`, and `correlation`; these require `pandas` DataFrames.
- `create_dashboard()` limits visible subplots to `len(datasets)` and hides unused axes.
- Performance monitoring is no-op when `codomyrmex.performance` is not installed.
- Zero-mock: all rendering uses real matplotlib/seaborn; `NotImplementedError` for unimplemented paths.

## Error Handling

- `finalize_plot()` raises `ValueError` if no figure exists.
- `save_plot()` catches all exceptions, logs error, returns `False`.
- Invalid data to `create_heatmap()` (non-2D) logs warning and returns `None`.
