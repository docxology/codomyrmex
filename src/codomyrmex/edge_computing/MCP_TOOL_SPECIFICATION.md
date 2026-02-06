# Edge Computing - MCP Tool Specification

This document defines the Model Context Protocol tools for the Edge Computing module, covering function deployment, node health monitoring, state synchronization, and cluster inventory.

## General Considerations

- **Latency Sensitivity**: Edge operations are designed for low-latency environments. Tool responses should be fast.
- **State Sync**: Synchronization uses version-based conflict resolution (highest version wins).
- **Node Lifecycle**: Nodes must be registered before functions can be deployed to them.

---

## Tool: `edge_deploy_function`

### 1. Tool Purpose and Description

Deploys a function to one or more edge nodes. Can target a specific node or broadcast to all nodes in the cluster.

### 2. Invocation Name

`edge_deploy_function`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `function_id` | `string` | Yes | Unique function identifier | `"fn-process-img"` |
| `function_name` | `string` | Yes | Human-readable function name | `"process-image"` |
| `node_id` | `string` | No | Target node (omit to deploy to all) | `"edge-01"` |
| `memory_mb` | `integer` | No | Memory allocation in MB (default: 128) | `256` |
| `timeout_seconds` | `integer` | No | Execution timeout (default: 30) | `60` |
| `environment` | `object` | No | Environment variables for the function | `{"MODEL": "yolo-v8"}` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"deployed"` or `"error"` | `"deployed"` |
| `function_id` | `string` | Deployed function ID | `"fn-process-img"` |
| `deployed_to` | `array[string]` | Node IDs where function was deployed | `["edge-01", "edge-02"]` |
| `deploy_count` | `integer` | Number of nodes | `2` |

### 5. Error Handling

- **Node Not Found**: Returns error if `node_id` is specified but not registered.
- **No Nodes Available**: Returns error if cluster has no registered nodes.
- **Duplicate Deploy**: Overwrites existing function with same ID on the node (not an error).

### 6. Idempotency

- **Idempotent**: Yes. Redeploying the same function overwrites the previous deployment.

### 7. Usage Examples

```json
{
  "tool_name": "edge_deploy_function",
  "arguments": {
    "function_id": "fn-process-img",
    "function_name": "process-image",
    "node_id": "edge-01",
    "memory_mb": 256,
    "timeout_seconds": 60
  }
}
```

```json
{
  "tool_name": "edge_deploy_function",
  "arguments": {
    "function_id": "fn-health-check",
    "function_name": "health-check"
  }
}
```

### 8. Security Considerations

- **Function Code**: The MCP tool deploys function metadata; actual handler code must be pre-registered in the runtime.
- **Environment Variables**: May contain secrets; ensure transport encryption.
- **Authorization**: Restrict deployment to authorized operators.

---

## Tool: `edge_node_status`

### 1. Tool Purpose and Description

Retrieves health and status information for one or all edge nodes, including last heartbeat, capabilities, and deployed functions.

### 2. Invocation Name

`edge_node_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `node_id` | `string` | No | Specific node (default: all nodes) | `"edge-01"` |
| `include_functions` | `boolean` | No | Include deployed function list (default: false) | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `nodes` | `array[object]` | Node status list | See below |
| `total_nodes` | `integer` | Total registered nodes | `5` |
| `online_count` | `integer` | Nodes with ONLINE status | `4` |

Each node object:

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `id` | `string` | Node ID | `"edge-01"` |
| `name` | `string` | Node name | `"warehouse-sensor"` |
| `status` | `string` | Current status | `"online"` |
| `location` | `string` | Physical location | `"Building A, Rack 3"` |
| `last_heartbeat` | `string` | ISO timestamp | `"2026-02-05T10:00:00Z"` |
| `capabilities` | `array[string]` | Node capabilities | `["gpu", "camera"]` |
| `functions` | `array[object]` | Deployed functions (if requested) | `[{"id": "fn-1", "name": "..."}]` |

### 5. Error Handling

- **Node Not Found**: Returns empty `nodes` array if `node_id` does not match.

### 6. Idempotency

- **Idempotent**: Yes. Read-only query.

### 7. Usage Examples

```json
{
  "tool_name": "edge_node_status",
  "arguments": {
    "node_id": "edge-01",
    "include_functions": true
  }
}
```

### 8. Security Considerations

- Read-only. Node locations, capabilities, and function lists may reveal infrastructure topology.

---

## Tool: `edge_sync`

### 1. Tool Purpose and Description

Triggers or queries state synchronization between edge nodes and the central cloud. Can push local changes, pull remote state, or report sync status.

### 2. Invocation Name

`edge_sync`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `action` | `string` | Yes | `"push"`, `"pull"`, `"status"`, or `"confirm"` | `"push"` |
| `node_id` | `string` | No | Target node for sync | `"edge-01"` |
| `data` | `object` | No | Data to sync (required for `push`) | `{"key": "value"}` |
| `version` | `integer` | No | Version number (required for `confirm`) | `5` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"synced"`, `"pending"`, `"confirmed"`, or `"error"` | `"synced"` |
| `version` | `integer` | Current state version | `5` |
| `checksum` | `string` | MD5 checksum of current state | `"a1b2c3d4..."` |
| `pending_changes` | `integer` | Number of unsynced changes | `0` |
| `last_sync` | `string` | ISO timestamp of last sync | `"2026-02-05T10:00:00Z"` |

### 5. Error Handling

- **No Local State**: `pull` or `status` with no existing state returns version 0.
- **Missing Data**: `push` without `data` returns error.
- **Version Conflict**: `pull` with a version older than local is a no-op (returns current state).

### 6. Idempotency

- **push**: Not idempotent (increments version).
- **pull**: Idempotent (applies only if remote is newer).
- **status**: Idempotent (read-only).
- **confirm**: Idempotent (confirming already-confirmed changes is a no-op).

### 7. Usage Examples

```json
{
  "tool_name": "edge_sync",
  "arguments": {
    "action": "push",
    "node_id": "edge-01",
    "data": {"sensor_readings": [22.5, 23.1, 21.8]}
  }
}
```

```json
{
  "tool_name": "edge_sync",
  "arguments": {
    "action": "status",
    "node_id": "edge-01"
  }
}
```

### 8. Security Considerations

- **Data Integrity**: Checksums verify state consistency. Validate checksums on both ends.
- **Transport Security**: Sync data may contain sensitive operational state; encrypt in transit.
- **Version Ordering**: Version-based resolution prevents stale writes but does not merge conflicts.

---

## Tool: `edge_list_nodes`

### 1. Tool Purpose and Description

Lists all registered edge nodes in the cluster, optionally filtered by status. A lightweight alternative to `edge_node_status` for inventory queries.

### 2. Invocation Name

`edge_list_nodes`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `status_filter` | `string` | No | Filter by status: `"online"`, `"offline"`, `"degraded"`, `"syncing"` | `"online"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `nodes` | `array[object]` | Minimal node list | See below |
| `total` | `integer` | Total matching nodes | `3` |

Each node object:

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `id` | `string` | Node ID | `"edge-01"` |
| `name` | `string` | Node name | `"warehouse-sensor"` |
| `status` | `string` | Current status | `"online"` |
| `location` | `string` | Physical location | `"Building A"` |

### 5. Error Handling

- **Invalid Status**: Returns error if `status_filter` is not a valid `EdgeNodeStatus` value.
- Returns empty `nodes` array if no nodes match the filter.

### 6. Idempotency

- **Idempotent**: Yes. Read-only query.

### 7. Usage Examples

```json
{
  "tool_name": "edge_list_nodes",
  "arguments": {
    "status_filter": "online"
  }
}
```

```json
{
  "tool_name": "edge_list_nodes",
  "arguments": {}
}
```

### 8. Security Considerations

- Read-only. Minimal data exposure compared to `edge_node_status`.
- Node IDs and locations may still reveal infrastructure details.

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Home**: [Root README](../../../README.md)
