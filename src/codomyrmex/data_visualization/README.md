# data_visualization

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Comprehensive data visualization module providing chart generation, plotting engines, Mermaid diagram generation, and Git repository visualization. Supports multiple chart types (line, bar, scatter, histogram, pie, heatmap, box plot, area chart), configurable styles and color palettes, and an advanced plotting engine with dashboard creation. Includes specialized visualizers for Git branch topology and commit timelines.


## Installation

```bash
uv pip install codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Core Functions

- **`get_available_styles()`** -- Return list of available chart style names from the `ChartStyle` enum
- **`get_available_palettes()`** -- Return list of available color palette names from the `ColorPalette` enum
- **`get_available_plot_types()`** -- Return list of supported plot type names from the `PlotType` enum
- **`create_heatmap()`** -- Generate a heatmap visualization from matrix data
- **`create_box_plot()`** -- Generate a box plot for statistical distribution display
- **`create_area_chart()`** -- Generate a filled area chart

### Submodules

- **`themes`** -- Chart theming and style configuration
- **`mermaid`** -- Mermaid diagram generation for flowcharts, sequences, and Git diagrams
- **`charts`** -- Individual chart type implementations (bar, line, scatter, histogram, pie, heatmap, box, area)

### Advanced Plotter (when matplotlib available)

- **`AdvancedPlotter`** -- Full-featured plotting engine with multi-panel dashboard support
- **`ChartStyle`** -- Enum of chart styles (DEFAULT, MINIMAL, MODERN, CLASSIC, DARK)
- **`ColorPalette`** -- Enum of color palettes (DEFAULT, VIRIDIS, PLASMA, CIVIDIS, RAINBOW)
- **`PlotType`** -- Enum of plot types (LINE, BAR, SCATTER, HISTOGRAM, PIE)
- **`PlotConfig` / `DataPoint` / `Dataset`** -- Configuration and data structures for the plotter
- **`create_line_plot()` / `create_scatter_plot()` / `create_bar_chart()` / `create_histogram()`** -- Convenience functions for common chart types
- **`create_dashboard()`** -- Generate a multi-chart dashboard layout

### Basic Charts (fallback when advanced plotter unavailable)

- **`LinePlot` / `ScatterPlot` / `BarChart` / `Histogram` / `PieChart`** -- Individual chart classes
- **`create_pie_chart()`** -- Generate a pie chart

### Git Visualization (optional)

- **`GitVisualizer`** -- Visualize Git repository structure and history
- **`create_git_tree_mermaid()` / `create_git_tree_png()`** -- Render Git trees as Mermaid or PNG
- **`visualize_git_repository()`** -- Full repository visualization

### Mermaid Generation (optional)

- **`MermaidDiagramGenerator`** -- Generate various Mermaid diagram types
- **`create_git_branch_diagram()`** -- Branch topology as Mermaid
- **`create_commit_timeline_diagram()`** -- Commit history timeline
- **`create_git_workflow_diagram()`** -- Git workflow as Mermaid
- **`create_repository_structure_diagram()`** -- Directory structure as Mermaid

## Directory Contents

- `charts/` -- Chart type implementations: `line_plot.py`, `bar_chart.py`, `scatter_plot.py`, `histogram.py`, `pie_chart.py`, `heatmap.py`, `box_plot.py`, `area_chart.py`, `plot_utils.py`
- `engines/` -- Advanced plotting engine (`advanced_plotter.py`, `plotter.py`)
- `git/` -- Git repository visualization (`git_visualizer.py`)
- `mermaid/` -- Mermaid diagram generator (`mermaid_generator.py`)
- `themes/` -- Chart theme definitions and style configuration
- `exceptions.py` -- Visualization-specific exceptions

## Quick Start

```python
from codomyrmex.data_visualization import get_available_styles, get_available_palettes, get_available_plot_types

result = get_available_styles()
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k data_visualization -v
```

## Navigation

- **Full Documentation**: [docs/modules/data_visualization/](../../../docs/modules/data_visualization/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
