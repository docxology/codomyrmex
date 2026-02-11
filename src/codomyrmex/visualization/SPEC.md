# Visualization - Functional Specification

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

To provide a single source of truth for system observability by visualizing the state of all active modules.

## Components

### 1. Dashboard Engine (`core/dashboard.py`)

- **Responsibility**: Aggregate visual elements.
- **Input**: List of Sections containing Plots or Components.
- **Output**: Rendered HTML file via `core/export.py`.

### 2. Report Engines (`reports/`)

- **Responsibility**: Orchestrate data fetching and dashboard creation.
- **Logic**:
    1. Instantiate domain engines (Ledger, Colony, CRM).
    2. Call domain visualizers to get data/plots.
    3. Add sections to `Dashboard`.
    4. Call `dashboard.render()`.

### 3. Plotting System (`plots/`)

- **Responsibility**: Abstraction over visualization libraries (Matplotlib, Mermaid).
- **Supported Types**:
  - Scatter Plot (`plots/scatter.py`)
  - Heatmap (`plots/heatmap.py`)
  - Mermaid Diagram (`plots/mermaid.py`)
- **Interface**: All plots inherit from `Plot` and implement `to_html()`.

### 4. Component System (`components/`)

- **Responsibility**: Reusable UI elements.
- **Components**:
  - `Card`: Metric display.
  - `Table`: Data grid.

## Extension Points

New modules should implement a `visualization` submodule or adapter that returns:

1. `codomyrmex.visualization.plots.Plot` subclasses.
2. `codomyrmex.visualization.components` instances.

Example Adapter:

```python
from codomyrmex.visualization import ScatterPlot

def plot_my_metric(data):
    return ScatterPlot("My Metric", data.x, data.y)
```
