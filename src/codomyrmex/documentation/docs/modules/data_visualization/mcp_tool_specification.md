# Data Visualization - MCP Tool Specification

This document specifies the MCP tools **currently implemented** in the Data Visualization module.

> **Note:** This spec was updated to reflect the actual implementation in `mcp_tools.py`.
> Previously documented per-chart-type tools (`create_heatmap`, `create_line_plot`, `create_scatter_plot`,
> `create_bar_chart`, `create_histogram`, `create_pie_chart`) are **not yet implemented** as MCP tools.
> The implementation uses a unified `generate_chart` tool with a `chart_type` parameter. See Planned Tools.

## General Considerations

- **Tool Integration**: Provides chart generation and HTML dashboard export.
- **Category**: `data_visualization`
- **Auto-discovered**: Yes (via `@mcp_tool` decorator in `mcp_tools.py`)

---

## Tool: `generate_chart`

### 1. Tool Purpose and Description

Generate a visualization chart of the specified type using provided data. Optionally saves the output to a file. Supports bar, pie, line, scatter, area, and histogram chart types.

### 2. Invocation Name

`generate_chart`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `chart_type` | `string` | Yes | One of: `'bar'`, `'pie'`, `'line'`, `'scatter'`, `'area'`, `'histogram'` | `"bar"` |
| `data` | `object` | Yes | Chart data (structure depends on `chart_type` — see examples) | `{"categories": [...], "values": [...]}` |
| `title` | `string` | No | Chart title. Default: `"Chart"` | `"Monthly Sales"` |
| `output_path` | `string` | No | File path to save the rendered output. If omitted, chart is returned in-memory only. | `"/tmp/chart.html"` |

**Data structure by chart_type:**

| `chart_type` | Notes |
|:-------------|:------|
| `bar` | `data` passed as positional argument to `dv.create_bar_chart(data, title=title)` |
| `pie`, `line`, `scatter`, `area`, `histogram` | `data` keys are unpacked as kwargs to the factory function |

### 4. Output Schema

| Field | Type | Description |
|:------|:-----|:------------|
| `status` | `string` | `"success"` or `"error"` |
| `rendered` | `boolean` | `true` if chart was generated (success only) |
| `chart_type` | `string` | The chart type that was generated |
| `chart` | `any` | The chart object or schema returned by the factory |
| `output_path` | `string` | Path where file was saved (only when `output_path` was provided) |
| `message` | `string` | Error details (on `"error"` status) |

### 5. Example Usage

```json
// Request:
{
  "chart_type": "bar",
  "data": {"categories": ["Q1", "Q2", "Q3"], "values": [100, 150, 120]},
  "title": "Quarterly Revenue"
}

// Response:
{
  "status": "success",
  "rendered": true,
  "chart_type": "bar",
  "chart": { "..." : "..." }
}
```

---

## Tool: `export_dashboard`

### 1. Tool Purpose and Description

Generate and export a comprehensive HTML dashboard report to a specified directory. Supports multiple report types for different domains.

### 2. Invocation Name

`export_dashboard`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `report_type` | `string` | No | One of: `'general'`, `'finance'`, `'marketing'`, `'logistics'`. Default: `"general"` | `"finance"` |
| `output_dir` | `string` | No | Directory to save the HTML report. Default: `"."` | `"/tmp/reports"` |

### 4. Output Schema

| Field | Type | Description |
|:------|:-----|:------------|
| `status` | `string` | `"success"` or `"error"` |
| `message` | `string` | Success or error description |
| `file_path` | `string` | Path of the generated HTML file (on success) |

### 5. Example Usage

```json
// Request:
{
  "report_type": "finance",
  "output_dir": "/tmp/dashboards"
}

// Response:
{
  "status": "success",
  "message": "Dashboard exported successfully",
  "file_path": "/tmp/dashboards/finance_report.html"
}
```

---

## Planned Tools (Not Yet Implemented as MCP)

The following per-chart-type tools are documented as future work. The underlying Python functions
exist in `src/codomyrmex/data_visualization/` but are not individually exposed as MCP tools yet.
Use `generate_chart` with the appropriate `chart_type` parameter instead.

| Tool Name | Equivalent `chart_type` |
|:----------|:------------------------|
| `create_bar_chart` | `"bar"` |
| `create_pie_chart` | `"pie"` |
| `create_line_plot` | `"line"` |
| `create_scatter_plot` | `"scatter"` |
| `create_histogram` | `"histogram"` |
| `create_heatmap` | *(no current equivalent — planned)* |
