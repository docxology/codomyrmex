# Charts Submodule - Agent Instructions

## Purpose

Provides chart type implementations for data visualization.

## Key Files

- `bar_chart.py` - Bar chart with customization options
- `line_plot.py` - Line plots with trend support
- `pie_chart.py` - Pie charts with percentage labels
- `histogram.py` - Histograms with bin configuration
- `scatter_plot.py` - Scatter plots with regression lines

## Agent Guidelines

- Use appropriate chart type for data being visualized
- Configure color themes via parent themes/ submodule
- All charts support matplotlib backend
- Export functions prefer PNG format by default

## Integration Points

- Import from `codomyrmex.data_visualization.charts`
- Uses engines/ for rendering utilities
- Themes applied from themes/ submodule
