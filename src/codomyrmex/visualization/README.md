# Visualization Module

**Version**: v0.3.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Central Visualization Module acts as the "Command Center" for the entire Codomyrmex ecosystem. It aggregates data visualizers from all specialized modules (Finance, Bio-Simulation, Governance, etc.) into a unified, interactive Executive Dashboard.

## Key Features

- **Unified Dashboarding**: Combines charts from different domains into a single view.
- **Multi-Format Support**: Generates HTML reports.
- **Modular Adapters**: Easy integration for new modules via standard interfaces.
- **Theming**: Centralized control over look-and-feel.
- **Pluggable Plots**: Support for Scatter, Heatmap, Mermaid diagrams, and more.
- **Extensible Components**: Reusable UI components like Cards and Tables.

## Architecture

The module is organized into submodules for better maintainability:

- `core/`: Core infrastructure.
  - `dashboard.py`: Base Dashboard class.
  - `layout.py`: Grid and Section layout logic.
  - `theme.py`: Theme and CSS definitions.
  - `export.py`: HTML rendering engine.
- `plots/`: Visualization implementations.
  - `scatter.py`: Scatter plots.
  - `heatmap.py`: Heatmaps.
  - `mermaid.py`: Mermaid diagram support.
  - `base.py`: Abstract base class for plots.
  - `violin.py`: Violin plots.
  - `radar.py`: Radar charts.
  - `candlestick.py`: Candlestick charts.
  - `funnel.py`: Funnel charts.
  - `sankey.py`: Sankey diagrams.
  - `wordcloud.py`: Word clouds.
  - `confusion_matrix.py`: Confusion matrices.
  - `treemap.py`: Tree maps.
  - `network.py`: Network graphs.
- `components/`: UI components.
  - `basic.py`: Card, Table, etc.
  - `media.py`: Image, Video.
  - `text.py`: TextBlock, CodeBlock.
  - `badge.py`: Status Badges.
  - `alert.py`: Alert Boxes.
  - `progress.py`: Progress Bars.
  - `timeline.py`: Timeline.
  - `statbox.py`: StatBox.
  - `chat_bubble.py`: Chat bubbles.
  - `json_view.py`: JSON viewer.
  - `heatmap_table.py`: Heatmap table.
- `reports/`: Domain-specific report generators.
  - `general.py`: Executive Dashboard implementation.
  - `base.py`: Abstract base class for reports.

## Usage

### Generating a Report

```python
from codomyrmex.visualization import GeneralSystemReport

# Create and save a report
report = GeneralSystemReport()
report_path = report.save("my_dashboard.html")
print(f"Dashboard generated at: {report_path}")
```

### Custom Dashboard

```python
from codomyrmex.visualization import Dashboard, ScatterPlot, Card

dashboard = Dashboard("My Custom Dashboard")

# Add a metric card
dashboard.add_section(
    "Key Metric", 
    Card(title="Active Users", value=1234)
)

# Add a plot
plot = ScatterPlot("User Growth", [1, 2, 3], [10, 20, 30])
dashboard.add_section("Growth Chart", plot)

# Render
dashboard.render("custom_dashboard.html")
```
