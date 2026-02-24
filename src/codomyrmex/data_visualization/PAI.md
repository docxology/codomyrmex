# Personal AI Infrastructure — Data Visualization Module

**Version**: v1.0.2 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Data Visualization module provides charting, dashboards, and visual reporting for
code metrics, performance data, and analytics. It generates interactive charts and
static visualizations for agent-produced data — benchmark results, coverage trends,
dependency graphs, and custom metric dashboards.

For PAI, the primary value is in the VERIFY phase: generating visual evidence that
ISC criteria are met (e.g., performance regression charts showing no slowdown) and in
LEARN phase for trend visualization across sessions.

## PAI Capabilities

### Chart Generation

Generate individual charts from structured data:

```python
import codomyrmex.data_visualization as dv

# Bar chart — test pass rates per module
chart = dv.create_bar_chart(
    {"labels": ["auth", "search", "events"], "values": [95, 100, 87]},
    title="Test Pass Rate by Module"
)

# Line plot — performance trend over N iterations
chart = dv.create_line_plot(x=[1, 2, 3, 4], y=[120, 118, 115, 113], title="Latency ms")

# Scatter plot — ISC coverage vs file complexity
chart = dv.create_scatter_plot(x=[...], y=[...], title="Complexity vs Coverage")

# Area chart — memory usage over time
chart = dv.create_area_chart(x=[...], y=[...], title="Memory Usage")

# Histogram — test durations distribution
chart = dv.create_histogram(data=[...], title="Test Duration Distribution")

# Pie chart — module layer breakdown
chart = dv.create_pie_chart(
    {"Auth": 12, "Search": 8, "Events": 5},
    title="Tool Distribution by Category"
)
```

### Dashboard Export

Compose multiple charts into a multi-panel HTML dashboard:

```python
from codomyrmex.data_visualization import generate_report

file_path = generate_report(output_dir="reports/", report_type="general")
# Generates: reports/dashboard_{timestamp}.html
```

Report types: `"general"`, `"finance"`, `"marketing"`, `"logistics"`

### Export Formats

Charts can be exported to:
- **PNG** — static images for documentation
- **SVG** — vector graphics for responsive dashboards
- **Interactive HTML** — Plotly-backed charts with hover/zoom

## MCP Tools

The following tools are auto-discovered via `@mcp_tool` and available through the PAI MCP bridge:

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `codomyrmex.generate_chart` | Generate a visualization chart and optionally save it | Safe | data_visualization |
| `codomyrmex.export_dashboard` | Generate and export a comprehensive HTML dashboard report | Safe | data_visualization |

### MCP Tool Usage Examples

**Generate a bar chart of ISC pass rates:**
```python
result = mcp_call("codomyrmex.generate_chart", {
    "chart_type": "bar",
    "data": {"labels": ["ISC-C1", "ISC-C2", "ISC-C3"], "values": [1, 1, 0]},
    "title": "ISC Verification Results",
    "output_path": "reports/isc_results.png"
})
# Returns: {"status": "success", "rendered": true, "chart_type": "bar"}
```

**Export a full HTML dashboard:**
```python
result = mcp_call("codomyrmex.export_dashboard", {
    "report_type": "general",
    "output_dir": "reports/"
})
# Returns: {"status": "success", "file_path": "reports/dashboard_20260224.html"}
```

## PAI Algorithm Phase Mapping

| Phase | Data Visualization Contribution | Key Functions |
|-------|---------------------------------|---------------|
| **OBSERVE** (1/7) | Visualize codebase metrics (coverage, complexity, test counts) | `create_bar_chart()`, `create_histogram()` |
| **VERIFY** (6/7) | Chart performance benchmark results; visualize ISC pass/fail matrix | `generate_chart` MCP tool, `create_scatter_plot()` |
| **LEARN** (7/7) | Generate trend visualizations for tracking metrics over sessions | `create_line_plot()`, `generate_report()` |

### Concrete PAI Usage Pattern

PAI LEARN phase can generate a trend chart after each Algorithm run:

```python
# PAI LEARN — persist ISC pass rate trend
session_results = [0.75, 0.82, 0.91, 1.0]  # Across 4 iterations
mcp_call("codomyrmex.generate_chart", {
    "chart_type": "line",
    "data": {"x": [1, 2, 3, 4], "y": session_results},
    "title": "ISC Pass Rate — Auth Refactor",
    "output_path": "~/.claude/MEMORY/WORK/auth-refactor/progress.png"
})
```

## PAI Configuration

| Environment Variable | Default | Purpose |
|---------------------|---------|---------|
| `CODOMYRMEX_VIZ_OUTPUT_DIR` | `reports/` | Default output directory for charts |
| `CODOMYRMEX_VIZ_BACKEND` | `plotly` | Rendering backend (`plotly`, `matplotlib`) |

## PAI Best Practices

1. **Use charts as ISC evidence**: For performance ISC criteria, generate a comparison
   chart (before/after benchmark) as the visual proof. Include the `output_path` so the
   chart is persisted alongside the PRD.

2. **Export dashboards at LEARN, not VERIFY**: Dashboards aggregate multiple metrics —
   run them in LEARN when all data is final, not mid-verification when data is partial.

3. **Keep chart data structured**: Pass `{"labels": [...], "values": [...]}` as the
   standard data format for bar and pie charts; `{"x": [...], "y": [...]}` for line,
   scatter, and area charts. Mixing formats requires the caller to adapt.

## Architecture Role

**Core Layer** — Consumed by `performance/` (benchmark visualization), `maintenance/`
(health dashboards), and the PAI dashboard.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **MCP Tools**: [mcp_tools.py](mcp_tools.py)
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
