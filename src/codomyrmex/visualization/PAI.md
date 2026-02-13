# Personal AI Infrastructure -- Visualization Module

**Version**: v0.3.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Visualization module is the **visual command center** for the entire Codomyrmex ecosystem. It provides a unified interface for creating dashboards, rendering 18+ plot types, assembling reusable UI components, and generating domain-specific reports (financial, marketing, logistics). Every other module that needs visual output depends on this module's plot and component library.

## PAI Capabilities

### Dashboard Creation

Build custom dashboards from plots and components:

```python
from codomyrmex.visualization import Dashboard, ScatterPlot, Card

dashboard = Dashboard("My Dashboard")
dashboard.add_section("Metric", Card(title="Users", value=1234))
dashboard.add_section("Growth", ScatterPlot("Growth", [1, 2, 3], [10, 20, 30]))
path = dashboard.render("output.html")
```

### Domain-Specific Reports

Generate complete HTML reports with one call:

```python
from codomyrmex.visualization import generate_report

# Options: "general", "finance", "marketing", "logistics"
path = generate_report(output_dir="reports", report_type="finance")
```

### Plot Library (18+ Types)

All plots render to HTML for dashboard embedding:

```python
from codomyrmex.visualization import (
    BarPlot, LinePlot, PieChart, CandlestickChart,
    FunnelChart, SankeyDiagram, NetworkGraph, MermaidDiagram,
)
```

### UI Components (11 Types)

Reusable components for dashboard assembly:

```python
from codomyrmex.visualization import (
    Card, Table, Badge, Alert, ProgressBar,
    Timeline, StatBox, ChatBubble, JsonView, HeatmapTable,
)
```

## Key Exports

| Export | Subpackage | Type | Purpose |
|--------|------------|------|---------|
| `Dashboard` | core | Class | Main dashboard container with grid layout and HTML rendering |
| `Grid` | core | Dataclass | Grid layout manager with configurable columns |
| `Theme` | core | Dataclass | Visual theme with CSS generation |
| `Plot` | plots | Abstract Class | Base class for all 18 plot types |
| `ScatterPlot` | plots | Class | Matplotlib scatter plot with base64 PNG embedding |
| `BarPlot` | plots | Class | Bar chart |
| `LinePlot` | plots | Class | Line chart with multi-dataset support |
| `CandlestickChart` | plots | Class | Financial OHLC chart |
| `MermaidDiagram` | plots | Class | Mermaid.js diagram (client-side rendering) |
| `NetworkGraph` | plots | Class | Network topology graph |
| `Card` | components | Dataclass | Simple metric display card |
| `Table` | components | Dataclass | HTML table with headers and rows |
| `StatBox` | components | Class | KPI stat box with trend indicator |
| `Alert` | components | Class | Alert box with severity levels |
| `Timeline` | components | Class | Chronological event timeline |
| `Report` | reports | Abstract Class | Base class for domain-specific reports |
| `GeneralSystemReport` | reports | Class | Executive dashboard report |
| `FinanceReport` | reports | Class | Financial overview report |
| `MarketingReport` | reports | Class | Marketing campaign analysis report |
| `LogisticsReport` | reports | Class | Supply chain and logistics report |
| `generate_report()` | top-level | Function | Convenience function for one-call report generation |

## PAI Algorithm Phase Mapping

| Phase | Visualization Module Contribution |
|-------|----------------------------------|
| **OBSERVE** | Dashboards and plots render system state for visual observation and monitoring |
| **PLAN** | Report templates (FinanceReport, LogisticsReport) structure visual planning artifacts |
| **EXECUTE** | `Dashboard.render()` and `Report.save()` execute HTML generation to disk |
| **VERIFY** | Visual verification is the primary role -- plots, charts, and dashboards make data patterns visible for human and agent review |
| **LEARN** | Generated reports capture historical snapshots; trend charts (LinePlot, CandlestickChart) visualize learning trajectories |

## Architecture Role

**Service Layer** -- This module is a critical cross-cutting concern. Almost every domain module (bio_simulation, finance, governance, relations, education) depends on it for visual output. It has no upward dependencies and must remain stable.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
