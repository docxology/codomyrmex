# Codomyrmex Agents -- src/codomyrmex/data_visualization/plots

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

A library of 19 plot types built on a common `BasePlot` dataclass. Each plot renders to HTML via `to_html()` (base64-encoded PNG from matplotlib) and supports `render()`, `save()`, and `to_dict()`. Plot types span statistical charts (bar, line, scatter, histogram, box, violin, heatmap), specialized visualizations (candlestick, gantt, funnel, sankey, radar, treemap, wordcloud, confusion matrix, network graph), area plots, pie charts, and Mermaid diagram wrappers.

## Key Components

| File | Class | Role |
|------|-------|------|
| `_base.py` | `BasePlot` | Abstract base: `to_html()` renders matplotlib figure to base64 PNG |
| `bar_chart.py` | `BarChart` | Bar chart from categories/values or (label, value) tuples |
| `line_plot.py` | `LinePlot` | Line plot from x/y data lists |
| `scatter.py` | `ScatterPlot` | Scatter plot with configurable marker size and colour |
| `histogram.py` | `Histogram` | Distribution histogram with bin count |
| `heatmap.py` | `Heatmap` | 2D heatmap with colormap and annotation |
| `box.py` | `BoxPlot` | Box-and-whisker plot |
| `violin.py` | `ViolinPlot` | Violin plot for distribution shape |
| `pie.py` | `PieChart` | Pie chart with labels and sizes |
| `area.py` | `AreaPlot` | Filled area chart |
| `candlestick.py` | `CandlestickChart` | Financial OHLC candlestick chart |
| `gantt.py` | `GanttChart` | Gantt chart for task scheduling |
| `funnel.py` | `FunnelChart` | Conversion funnel chart |
| `sankey.py` | `SankeyDiagram` | Flow diagram with source-target-value links |
| `radar.py` | `RadarChart` | Radar/spider chart |
| `treemap.py` | `TreeMap` | Hierarchical treemap |
| `wordcloud.py` | `WordCloud` | Word cloud from text data |
| `confusion_matrix.py` | `ConfusionMatrix` | ML confusion matrix heatmap |
| `network.py` | `NetworkGraph` | Network/graph visualization |
| `mermaid.py` | `MermaidDiagram` | Wraps mermaid flowchart builder for HTML output |

## Operating Contracts

- All plot classes inherit from `BasePlot` and override `_render_figure(fig, ax)`.
- `to_html()` returns an `<img>` tag with inline base64 PNG data -- no external files needed.
- `save(output_path)` writes a minimal HTML document wrapping the base64 image.
- `to_dict()` returns serialized metadata including `type`, `title`, `width`, `height`, `data_count`.
- `__str__()` delegates to `to_html()` for direct template interpolation.
- matplotlib uses `"Agg"` backend (non-interactive) to support headless rendering.

## Integration Points

- **Depends on**: `matplotlib` (Agg backend), Python stdlib (`base64`, `io`, `dataclasses`)
- **Used by**: `data_visualization.reports` (e.g., `LogisticsReport` uses `SankeyDiagram`), dashboard composition

## Navigation

- **Parent**: [data_visualization](../README.md)
- **Root**: [Root](../../../../README.md)
