# Visualization - Functional Specification

**Version**: v0.3.0 | **Status**: Active | **Last Updated**: February 2026

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
- **Standard Types**:
  - `ScatterPlot`: XY scatter.
  - `BarPlot`: Bar chart (vertical/horizontal).
  - `LinePlot`: Line chart.
  - `Histogram`: Frequency distribution.
  - `PieChart`: Proportional data.
  - `BoxPlot`: Statistical distribution.
  - `AreaPlot`: Quantitative trend.
  - `ViolinPlot`: Data density.
  - `RadarChart`: Multivariate comparison.
  - `CandlestickChart`: Financial OHLC.
  - `GanttChart`: Project timeline.
  - `FunnelChart`: Conversion pipelines.
  - `SankeyDiagram`: Flow visualization.
  - `WordCloud`: Text frequency visualization.
  - `ConfusionMatrix`: Classification performance.
  - `TreeMap`: Hierarchical data.
  - `NetworkGraph`: Node-link relationships.
- **Interface**: All plots inherit from `Plot` and implement `to_html()`.

### 4. Component System (`components/`)

- **Responsibility**: Reusable UI elements.
- **Components**:
  - `Card`: Metric display.
  - `Table`: Data grid.
  - `Image`: Embed local/remote images.
  - `Video`: Embed video files.
  - `TextBlock`: Markdown/HTML text.
  - `CodeBlock`: Syntax-highlighted code.
  - `Badge`: Status indicator.
  - `Alert`: Contextual message box.
  - `ProgressBar`: Visual completion tracker.
  - `Timeline`: Vertical event list.
  - `StatBox`: Metric with trend indicator.
  - `ChatBubble`: Conversation display.
  - `JsonView`: Collapsible JSON data.
  - `HeatmapTable`: Color-coded data grid.

## Extension Points

New modules should implement a `visualization` submodule or adapter that returns:

1. `codomyrmex.visualization.plots.Plot` subclasses.
2. `codomyrmex.visualization.components` instances.
