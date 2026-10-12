# Edge Computing - MCP Tool Specification

This document defines the Model Context Protocol tools for the Edge Computing module. They are defined with `@mcp_tool` in `mcp_tools.py` and surfaced by the PAI MCP bridge as `codomyrmex.<name>`. All three tools are read-only.

## General Considerations

- **No shared cluster**: `edge_computing_cluster_health` and `edge_computing_health_check` build a new `EdgeCluster` or `HealthMonitor` on every call, so they report an empty cluster (all counts `0`). Deploying functions, registering nodes and synchronising state are available only from the Python API (`EdgeCluster`, `HealthMonitor`).
- **Error Handling**: Tools catch exceptions and return `{"status": "error", "message": "<description>"}`.

---

## Tool: `edge_computing_cluster_health`

### 1. Tool Purpose and Description

Returns the health summary of an edge cluster: node counts by state, deployed functions and invocations.

### 2. Invocation Name

`edge_computing_cluster_health`

### 3. Input Schema (Parameters)

None.

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "total_nodes": 0,
  "online": 0,
  "draining": 0,
  "total_functions": 0,
  "total_invocations": 0,
  "nodes": []
}
```

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `edge_computing_list_capabilities`

### 1. Tool Purpose and Description

Lists the edge node statuses, deployment strategies and schedule types the module supports.

### 2. Invocation Name

`edge_computing_list_capabilities`

### 3. Input Schema (Parameters)

None.

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "node_statuses": ["online", "offline", "degraded", "syncing", "maintenance"],
  "deployment_strategies": ["rolling", "blue_green", "canary"],
  "schedule_types": ["once", "interval", "cron_like"]
}
```

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `edge_computing_health_check`

### 1. Tool Purpose and Description

Creates a `HealthMonitor` with the given heartbeat timeout and returns its summary.

### 2. Invocation Name

`edge_computing_health_check`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `heartbeat_timeout_seconds` | `number` | No | Seconds before a node is considered stale (default `60.0`) | `30.0` |

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "monitored_nodes": 0,
  "total_checks": 0,
  "timeout_seconds": 60.0
}
```

### 5. Idempotency

- **Idempotent**: Yes

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Home**: [Root README](../../../README.md)

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
