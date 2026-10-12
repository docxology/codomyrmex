# Data Lineage - MCP Tool Specification

This document specifies the Model Context Protocol (MCP) tools of the `data_lineage` module. They are defined with `@mcp_tool` in `mcp_tools.py` and surfaced by the PAI MCP bridge as `codomyrmex.<name>`.

## General Considerations for Data Lineage Tools

- **No shared state**: Each call creates a new, empty `DataLineage` (or `LineageGraph`). Nodes registered by one call are not visible to the next, so a transformation that references datasets from an earlier call fails with `"Source node '<id>' does not exist in graph."`. Build multi-step lineage with the Python `DataLineage` API.
- **Error Handling**: Tools catch exceptions and return `{"status": "error", "message": "<description>"}`.
- **Security**: No file or network access; tools only build in-memory graphs.

---

## Tool: `data_lineage_track`

### 1. Tool Purpose and Description

Registers a dataset or a transformation node in a lineage graph.

### 2. Invocation Name

`data_lineage_track`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `event_type` | `string` | Yes | `"dataset"` or `"transformation"` | `"dataset"` |
| `node_id` | `string` | Yes | Unique node identifier | `"raw_events"` |
| `name` | `string` | Yes | Human-readable name | `"Raw events"` |
| `inputs` | `array[string]` | No | Input node IDs (transformations only) | `["raw_events"]` |
| `outputs` | `array[string]` | No | Output node IDs (transformations only) | `["clean_events"]` |
| `location` | `string` | No | Dataset location (datasets only, default `""`) | `"s3://bucket/raw"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `node_id` | `string` | ID of the registered node | `"raw_events"` |
| `node_type` | `string` | Node type value | `"dataset"` |
| `message` | `string` | Error description (only on error) | `"Unknown event_type: model. Use 'dataset' or 'transformation'."` |

### 5. Idempotency

- **Idempotent**: Yes, because nothing persists between calls.

### 6. Usage Examples (for MCP context)

```json
{
  "tool_name": "data_lineage_track",
  "arguments": {
    "event_type": "dataset",
    "node_id": "raw_events",
    "name": "Raw events",
    "location": "s3://bucket/raw"
  }
}
```

---

## Tool: `data_lineage_analyze_impact`

### 1. Tool Purpose and Description

Registers `node_id` as a dataset in a new lineage graph and reports the downstream impact of changing it. Because the graph is new, the result has no affected nodes.

### 2. Invocation Name

`data_lineage_analyze_impact`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `node_id` | `string` | Yes | Node to analyse | `"raw_events"` |

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "source_node": "raw_events",
  "total_affected": 0,
  "risk_level": "low",
  "affected_datasets": [],
  "affected_models": [],
  "affected_transformations": []
}
```

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `data_lineage_validate_graph`

### 1. Tool Purpose and Description

Creates a `LineageGraph`, checks it for cycles and returns its statistics. The graph is new and empty on every call.

### 2. Invocation Name

`data_lineage_validate_graph`

### 3. Input Schema (Parameters)

None.

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "node_count": 0,
  "edge_count": 0,
  "has_cycles": false,
  "cycle_nodes": [],
  "leaf_node_count": 0
}
```

### 5. Idempotency

- **Idempotent**: Yes

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
