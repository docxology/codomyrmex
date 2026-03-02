# Plots -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Nineteen plot types sharing a common `BasePlot` base class. Each plot renders to inline HTML (base64-encoded PNG) using the matplotlib Agg backend for headless environments. The module provides a uniform API (`to_html()`, `render()`, `save()`, `to_dict()`) across all chart types.

## Architecture

```
BasePlot (@dataclass)
  ├── title, width, height, data, options
  ├── to_html()          -- matplotlib -> base64 PNG -> <img> tag
  ├── render()           -- lightweight HTML placeholder
  ├── save(path)         -- write HTML document to file
  ├── to_dict()          -- serialize metadata
  └── _render_figure()   -- override point for subclasses
       |
       ├── BarChart, LinePlot, ScatterPlot, Histogram, PieChart
       ├── Heatmap, BoxPlot, ViolinPlot, AreaPlot
       ├── CandlestickChart, GanttChart, FunnelChart
       ├── SankeyDiagram, RadarChart, TreeMap, WordCloud
       ├── ConfusionMatrix, NetworkGraph
       └── MermaidDiagram
```

## Key Classes

### `BasePlot`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `to_html` | -- | `str` | Render as `<img src="data:image/png;base64,...">` |
| `render` | -- | `str` | Lightweight `<div>` placeholder |
| `save` | `output_path: str` | `str` | Write HTML document to file, return path |
| `to_dict` | -- | `dict` | `{type, title, width, height, data_count}` |
| `_render_figure` | `fig, ax` | `None` | Override in subclasses to draw on axes |
| `_fig_to_base64` | `fig` | `str` | Static: convert figure to base64 string |

### Plot Subclasses (common pattern)

Each subclass adds domain-specific fields and overrides `_render_figure()`:

| Class | Key Fields | Rendering |
|-------|-----------|-----------|
| `BarChart` | `categories`, `values` | `ax.bar()` |
| `LinePlot` | `x_data`, `y_data` | `ax.plot()` |
| `ScatterPlot` | `x_data`, `y_data`, `sizes`, `colors` | `ax.scatter()` |
| `Histogram` | `data`, `bins` | `ax.hist()` |
| `PieChart` | `labels`, `sizes` | `ax.pie()` |
| `Heatmap` | `data` (2D), `cmap` | `ax.imshow()` |
| `BoxPlot` | `data` (list of lists) | `ax.boxplot()` |
| `ViolinPlot` | `data` (list of lists) | `ax.violinplot()` |
| `AreaPlot` | `x_data`, `y_data` | `ax.fill_between()` |
| `CandlestickChart` | OHLC data | Custom bar rendering |
| `GanttChart` | `tasks` (name, start, duration) | `ax.barh()` |
| `FunnelChart` | `stages`, `values` | Horizontal bars |
| `SankeyDiagram` | `links` (source, target, value) | Flow lines |
| `RadarChart` | `categories`, `values` | Polar plot |
| `TreeMap` | `labels`, `sizes` | Squarified rectangles |
| `WordCloud` | `words` dict | Text-sized layout |
| `ConfusionMatrix` | `matrix`, `labels` | Annotated heatmap |
| `NetworkGraph` | `nodes`, `edges` | Force-directed layout |
| `MermaidDiagram` | `diagram_type`, nodes/links | Mermaid text output |

## Dependencies

- **Internal**: `data_visualization.mermaid` (for `MermaidDiagram` plot type)
- **External**: `matplotlib` (Agg backend required)

## Constraints

- All plots use `matplotlib.use("Agg")` for non-interactive rendering.
- Figure dimensions are in pixels: `figsize=(width/100, height/100)` at 100 DPI.
- `to_html()` always calls `plt.close(fig)` to prevent memory leaks.
- Zero-mock: real matplotlib rendering only; `NotImplementedError` for unimplemented paths.

## Error Handling

- `BasePlot._render_figure()` renders a centered text label as fallback if not overridden.
- `save()` delegates to `Path.write_text()`; exceptions propagate to caller.
- Empty data results in blank or minimal plots (no exceptions raised).
