# Networks - MCP Tool Specification

This document outlines the specification for tools within the Networks module that are intended to be integrated with the Model Context Protocol (MCP).

## General Considerations

- **Dependencies**: Requires the `logging_monitoring` module. Ensure `setup_logging()` is called at startup.
- **Initialization**: No module-level initialization required beyond standard import.
- **Error Handling**: Errors are logged via `logging_monitoring`. Tools return an `{"error": "description"}` object on failure.

---

## Tool: `network_get_neighbors`

### 1. Tool Purpose and Description

Query the neighbors of a node in a network. Returns all node IDs connected to the specified node via inbound or outbound edges. Useful for agents exploring graph topology, dependency analysis, and traversal planning.

### 2. Invocation Name

`network_get_neighbors`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `network_name` | `string` | Yes | Name of the network to query | `"module_deps"` |
| `node_id` | `string` | Yes | ID of the node whose neighbors to retrieve | `"agents"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | "success" or "error" | `"success"` |
| `node_id` | `string` | The queried node ID | `"agents"` |
| `neighbors` | `array[string]` | List of neighboring node IDs | `["logging", "cli"]` |
| `count` | `integer` | Number of neighbors | `2` |

### 5. Error Handling

- **Node Not Found**: Returns error if `node_id` does not exist in the network.
- **Network Not Found**: Returns error if no network with `network_name` is registered.

### 6. Idempotency

- **Idempotent**: Yes. Repeated calls with the same parameters return the same result without side effects.

### 7. Usage Examples

```json
{
  "tool_name": "network_get_neighbors",
  "arguments": {
    "network_name": "module_deps",
    "node_id": "agents"
  }
}
```

### 8. Security Considerations

- **Input Validation**: `node_id` and `network_name` are validated as non-empty strings.
- **Permissions**: Read-only operation; no file system or network access.
- **Data Handling**: No sensitive data is processed or logged beyond node identifiers.

---

## Tool: `network_add_node`

### 1. Tool Purpose and Description

Add a node to an existing network. Enables agents to dynamically construct graph topologies during planning and build phases.

### 2. Invocation Name

`network_add_node`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `network_name` | `string` | Yes | Name of the target network | `"module_deps"` |
| `node_id` | `string` | Yes | Unique identifier for the new node | `"networks"` |
| `data` | `any` | No | Payload data for the node | `"Core"` |
| `attributes` | `object` | No | Arbitrary key-value attributes | `{"layer": 2}` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | "success", "duplicate", or "error" | `"success"` |
| `node_id` | `string` | The created node ID | `"networks"` |
| `message` | `string` | Human-readable result message | `"Node 'networks' added"` |

### 5. Error Handling

- **Duplicate Node**: Returns status "duplicate" if node ID already exists (no-op).
- **Network Not Found**: Returns error if no network with `network_name` is registered.

### 6. Idempotency

- **Idempotent**: Yes. Adding an existing node is a no-op.

### 7. Usage Examples

```json
{
  "tool_name": "network_add_node",
  "arguments": {
    "network_name": "module_deps",
    "node_id": "networks",
    "data": "Core",
    "attributes": {"layer": 2}
  }
}
```

### 8. Security Considerations

- **Input Validation**: `node_id` validated as non-empty string. `attributes` validated as a flat key-value object.
- **Permissions**: Mutates in-memory state only; no file system or network access.

---

## Tool: `network_add_edge`

### 1. Tool Purpose and Description

Add a directed, weighted edge between two existing nodes in a network. Enables agents to build graph relationships incrementally.

### 2. Invocation Name

`network_add_edge`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `network_name` | `string` | Yes | Name of the target network | `"module_deps"` |
| `source` | `string` | Yes | Source node ID | `"agents"` |
| `target` | `string` | Yes | Target node ID | `"logging"` |
| `weight` | `float` | No | Edge weight (default: 1.0) | `1.0` |
| `attributes` | `object` | No | Arbitrary key-value attributes | `{"relation": "depends_on"}` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | "success" or "error" | `"success"` |
| `source` | `string` | Source node ID | `"agents"` |
| `target` | `string` | Target node ID | `"logging"` |
| `weight` | `float` | Edge weight | `1.0` |

### 5. Error Handling

- **Node Not Found**: Returns error if either `source` or `target` node does not exist.
- **Network Not Found**: Returns error if no network with `network_name` is registered.

### 6. Idempotency

- **Idempotent**: No. Each call adds a new edge, even if an identical edge already exists.

### 7. Usage Examples

```json
{
  "tool_name": "network_add_edge",
  "arguments": {
    "network_name": "module_deps",
    "source": "agents",
    "target": "logging",
    "weight": 1.0,
    "attributes": {"relation": "depends_on"}
  }
}
```

### 8. Security Considerations

- **Input Validation**: `source` and `target` validated as non-empty strings. `weight` validated as numeric.
- **Permissions**: Mutates in-memory state only; no file system or network access.

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
