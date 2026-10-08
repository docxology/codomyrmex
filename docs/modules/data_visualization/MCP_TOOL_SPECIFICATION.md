# Data Visualization - MCP Tool Specification

This document specifies the MCP tools implemented in the Data Visualization module. They are defined with `@mcp_tool` and surfaced by the PAI MCP bridge as `codomyrmex.<name>`.

> **Note:** Charts are produced by the single `generate_chart` tool with a `chart_type` parameter. The per-chart Python functions (`create_bar_chart`, `create_line_plot`, ...) are not MCP tools themselves; see [Chart Functions Without MCP Tools](#chart-functions-without-mcp-tools).

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
| :--- | :--- | :--- | :--- | :--- |
| `chart_type` | `string` | Yes | One of: `'bar'`, `'pie'`, `'line'`, `'scatter'`, `'area'`, `'histogram'` | `"bar"` |
| `data` | `object` | Yes | Chart data (structure depends on `chart_type` — see examples) | `{"categories": [...], "values": [...]}` |
| `title` | `string` | No | Chart title. Default: `"Chart"` | `"Monthly Sales"` |
| `output_path` | `string` | No | File path to save the rendered output. If omitted, chart is returned in-memory only. | `"/tmp/chart.html"` |

**Data structure by chart_type:**

| `chart_type` | Factory called with `**data` |
| :--- | :--- |
| `bar` | `create_bar_chart` |
| `pie` | `create_pie_chart` |
| `line` | `create_line_plot` |
| `scatter` | `create_scatter_plot` |
| `area` | `create_area_chart` |
| `histogram` | `create_histogram` |

For every chart type the keys of `data` are passed as keyword arguments to the factory, with `title` added when `data` does not set it. Any other `chart_type` returns `{"status": "error", "message": "Unsupported chart type: <type>"}`. When `output_path` is given, the string form of the factory's result is written to that file.

### 4. Output Schema

| Field | Type | Description |
| :--- | :--- | :--- |
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
| :--- | :--- | :--- | :--- | :--- |
| `report_type` | `string` | No | One of: `'general'`, `'finance'`, `'marketing'`, `'logistics'`. Default: `"general"` | `"finance"` |
| `output_dir` | `string` | No | Directory to save the HTML report. Default: `"."` | `"/tmp/reports"` |

### 4. Output Schema

| Field | Type | Description |
| :--- | :--- | :--- |
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

## Mermaid Diagram Tools

`mermaid/mermaid_generator.py` also defines `@mcp_tool` functions. Each returns Mermaid diagram source as a string and saves it when `output_path` is given:

| Tool | Parameters |
| :--- | :--- |
| `create_git_branch_diagram` | `branches`, `commits`, `title` (default `"Git Branch Diagram"`), `output_path` |
| `create_git_workflow_diagram` | `workflow_steps`, `title` (default `"Git Workflow"`), `output_path` |
| `create_repository_structure_diagram` | `repo_structure`, `title` (default `"Repository Structure"`), `output_path` |
| `create_commit_timeline_diagram` | `commits`, `title` (default `"Commit Timeline"`), `output_path` |

All parameters are optional.

---

## Chart Functions Without MCP Tools

The chart factories `create_bar_chart`, `create_pie_chart`, `create_line_plot`, `create_scatter_plot`, `create_area_chart` and `create_histogram` are reached through `generate_chart`. Other Python functions such as `create_heatmap` and `create_box_plot` have no MCP tool and no `chart_type`; call them from Python.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
