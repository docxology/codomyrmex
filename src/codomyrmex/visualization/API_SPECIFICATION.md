# Visualization - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the Visualization module. This is the central visualization engine for the Codomyrmex ecosystem, providing a unified interface for creating dashboards, rendering 18+ plot types, assembling UI components, and generating domain-specific reports. The module is organized into four subpackages: `core/`, `plots/`, `components/`, and `reports/`.

---

## Subpackage: `core/`

Core infrastructure for dashboard creation, layout management, theming, and HTML export.

### Class: `Dashboard`

- **Description**: Base class for creating interactive dashboards. Manages a grid of sections and renders them to HTML.
- **Module**: `codomyrmex.visualization.core.dashboard`
- **Parameters/Arguments** (constructor):
    - `title` (str, optional): Dashboard title. Defaults to `"Codomyrmex Dashboard"`
    - `theme` (Theme, optional): Theme instance for styling. Defaults to `DEFAULT_THEME`
- **Attributes**:
    - `title` (str): Dashboard title
    - `theme` (Theme): Active theme
    - `grid` (Grid): The layout grid containing all sections
- **Methods**:
    - `add_section(title: str, content: Any, full_width: bool = False, description: str = None) -> None`: Add a named section to the dashboard grid.
    - `render(output_path: str) -> str`: Render the dashboard to an HTML file. Returns the absolute path to the generated file.

### Class: `Grid` (dataclass)

- **Description**: Represents a grid layout for the dashboard. Contains an ordered list of sections.
- **Module**: `codomyrmex.visualization.core.layout`
- **Parameters/Arguments** (constructor):
    - `columns` (int, optional): Number of columns in the grid. Defaults to `2`
    - `sections` (List[Section], optional): Pre-populated sections. Defaults to `[]`
- **Methods**:
    - `add_section(title: str, content: Any, full_width: bool = False, description: Optional[str] = None) -> None`: Add a section to the grid. Full-width sections span 100%; otherwise width is `100/columns`%.

### Class: `Section` (dataclass)

- **Description**: A single section within a grid layout.
- **Module**: `codomyrmex.visualization.core.layout`
- **Parameters/Arguments** (constructor):
    - `title` (str): Section title
    - `content` (Any): Content to render (HTML string, Plot object, Component, etc.)
    - `width` (str, optional): CSS width string. Defaults to `"100%"`
    - `description` (Optional[str], optional): Optional description text. Defaults to `None`

### Class: `Theme` (dataclass)

- **Description**: Defines the visual theme for dashboards and reports. Generates CSS from color and typography settings.
- **Module**: `codomyrmex.visualization.core.theme`
- **Parameters/Arguments** (constructor):
    - `primary` (str, optional): Primary color. Defaults to `"#2c3e50"`
    - `secondary` (str, optional): Secondary color. Defaults to `"#95a5a6"`
    - `accent` (str, optional): Accent color. Defaults to `"#e74c3c"`
    - `background` (str, optional): Background color. Defaults to `"#ecf0f1"`
    - `text` (str, optional): Text color. Defaults to `"#2c3e50"`
    - `font_family` (str, optional): Font stack. Defaults to `"'Segoe UI', sans-serif"`
- **Properties**:
    - `css` (str): Generated CSS stylesheet string.
- **Methods**:
    - `to_dict() -> Dict[str, Any]`: Serialize theme to dictionary.

### Function: `render_html(grid: Grid, title: str, output_path: Path, theme: Theme = DEFAULT_THEME) -> str`

- **Description**: Renders a Grid layout to a complete HTML file with Mermaid.js support.
- **Module**: `codomyrmex.visualization.core.export`
- **Parameters/Arguments**:
    - `grid` (Grid): The grid containing sections to render
    - `title` (str): Page title
    - `output_path` (Path): Path to write the HTML file
    - `theme` (Theme, optional): Theme for styling. Defaults to `DEFAULT_THEME`
- **Returns/Response**: `str` - Absolute path to the generated HTML file.

---

## Subpackage: `plots/`

18 plot types, all inheriting from the abstract `Plot` base class.

### Class: `Plot` (abstract)

- **Description**: Abstract base class for all visualization plots. Provides a common interface for rendering and HTML embedding.
- **Module**: `codomyrmex.visualization.plots.base`
- **Parameters/Arguments** (constructor):
    - `title` (str): Plot title
    - `data` (Any): Plot data (type varies by subclass)
- **Abstract Methods**:
    - `render() -> Any`: Render the plot (returns matplotlib Figure, HTML string, etc.).
- **Methods**:
    - `to_html() -> str`: Returns an HTML representation of the plot.
    - `__str__() -> str`: Returns `to_html()` output for string conversion.

### Plot Types

All plot classes inherit from `Plot` and are importable from `codomyrmex.visualization`.

| Class | Constructor Parameters | Description |
|-------|----------------------|-------------|
| `ScatterPlot` | `title: str, x_data: List[float], y_data: List[float], x_label: str = "X", y_label: str = "Y"` | Scatter plot via Matplotlib, renders to base64 PNG |
| `BarPlot` | `title: str, categories: list, values: list` | Bar chart |
| `LinePlot` | `title: str, x_labels: list, datasets: list, legend: list` | Line chart with multiple datasets |
| `Histogram` | `title: str, data: list, bins: int` | Histogram distribution |
| `PieChart` | `title: str, labels: list, sizes: list` | Pie/donut chart |
| `BoxPlot` | `title: str, data: list` | Box-and-whisker plot |
| `AreaPlot` | `title: str, x_data: list, y_data: list` | Filled area chart |
| `ViolinPlot` | `title: str, data: list` | Violin distribution plot |
| `RadarChart` | `title: str, categories: list, values: list` | Radar/spider chart |
| `CandlestickChart` | `title: str, dates: list, opens: list, highs: list, lows: list, closes: list` | Financial OHLC chart |
| `GanttChart` | `title: str, tasks: list, starts: list, durations: list` | Gantt schedule chart |
| `FunnelChart` | `title: str, stages: list, values: list` | Conversion funnel |
| `SankeyDiagram` | `title: str, links: list` | Flow/Sankey diagram |
| `WordCloud` | `title: str, terms: list` | Word cloud from (term, weight) pairs |
| `ConfusionMatrix` | `title: str, matrix: list, labels: list` | ML confusion matrix |
| `TreeMap` | `title: str, data: list` | Hierarchical treemap |
| `NetworkGraph` | `title: str, nodes: list, edges: list` | Network topology graph |
| `Heatmap` | `title: str, data: list` | 2D heatmap |
| `MermaidDiagram` | `title: str, definition: str` | Mermaid.js diagram (rendered client-side) |

---

## Subpackage: `components/`

Reusable UI components for dashboard assembly.

| Class | Module | Constructor Parameters | Description |
|-------|--------|----------------------|-------------|
| `Card` | `basic` | `title: str, value: Any, description: str = ""` | Simple metric card |
| `Table` | `basic` | `headers: list[str], rows: list[list[Any]]` | HTML table |
| `Image` | `media` | `src: str, alt: str` | Image embed |
| `Video` | `media` | `src: str` | Video embed |
| `TextBlock` | `text` | `content: str` | Rich text block |
| `CodeBlock` | `text` | `code: str, language: str` | Syntax-highlighted code |
| `Badge` | `badge` | `label: str, variant: str` | Status badge (success, primary, warning, etc.) |
| `Alert` | `alert` | `message: str, level: str` | Alert box (success, warning, danger, info) |
| `ProgressBar` | `progress` | `value: float, max_value: float, label: str = "", color: str = ""` | Progress indicator |
| `Timeline` | `timeline` | `events: List[TimelineEvent]` | Chronological timeline |
| `TimelineEvent` | `timeline` | `timestamp: str, title: str, description: str = "", icon: str = ""` | Single event in a timeline |
| `StatBox` | `statbox` | `label: str, value: str, change: str, direction: str` | KPI stat box with trend |
| `ChatBubble` | `chat_bubble` | `sender: str, message: str, timestamp: str` | Chat message bubble |
| `JsonView` | `json_view` | `data: dict` | Formatted JSON viewer |
| `HeatmapTable` | `heatmap_table` | `headers: list, rows: list, values: list` | Table with heatmap coloring |

---

## Subpackage: `reports/`

Domain-specific report generators that extend the abstract `Report` base class.

### Class: `Report` (abstract)

- **Description**: Abstract base class for domain-specific reports. Wraps a `Dashboard` instance and provides generate/save lifecycle.
- **Module**: `codomyrmex.visualization.reports.base`
- **Parameters/Arguments** (constructor):
    - `title` (str): Report title
- **Attributes**:
    - `dashboard` (Dashboard): The underlying dashboard instance
- **Abstract Methods**:
    - `generate() -> None`: Populate the dashboard with data and plots.
- **Methods**:
    - `save(output_path: str) -> str`: Generate the report and save to HTML. Returns the absolute file path.

### Report Types

| Class | Title | Description |
|-------|-------|-------------|
| `GeneralSystemReport` | "Codomyrmex Executive Dashboard" | Overview with finance, bio-sim, relations, and education sections |
| `FinanceReport` | "Financial Overview" | KPI stat boxes, candlestick chart, revenue trend, expense breakdown |
| `MarketingReport` | "Marketing Analysis" | Campaign badges, conversion funnel, demographics pie chart, sentiment word cloud, campaign timeline |
| `LogisticsReport` | "Logistics & Operations" | System alerts, fleet progress bar, Sankey supply chain, Gantt schedule, network topology |

### Function: `generate_report(output_dir: str = "report_output", report_type: str = "general") -> str`

- **Description**: Convenience function for generating and saving reports. Supports report types: `"general"`, `"finance"`, `"marketing"`, `"logistics"`.
- **Module**: `codomyrmex.visualization` (top-level)
- **Parameters/Arguments**:
    - `output_dir` (str, optional): Directory to save the report. Defaults to `"report_output"`
    - `report_type` (str, optional): Type of report to generate. Defaults to `"general"`
- **Returns/Response**: `str` - Path to the saved HTML report file.

---

## Authentication & Authorization

Not applicable for this internal visualization module.

## Rate Limiting

Not applicable for this internal visualization module.

## Versioning

This module follows the general versioning strategy of the Codomyrmex project. API stability is aimed for, with changes documented in the CHANGELOG.md.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
