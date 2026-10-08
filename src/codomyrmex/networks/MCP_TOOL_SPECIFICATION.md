# Networks - MCP Tool Specification

This document specifies the Model Context Protocol (MCP) tools of the Networks module. They are defined with `@mcp_tool` in `mcp_tools.py` and surfaced by the PAI MCP bridge as `codomyrmex.<name>`.

## General Considerations

- **Stateless graphs**: Each tool builds a new `Network` from the `nodes` and `edges` arguments; no named network is stored between calls. Edges are `[source, target]` pairs, and pairs with fewer than two items are ignored.
- **Error Handling**: Tools catch exceptions and return `{"status": "error", "message": "<description>"}`.
- **Security**: Pure in-memory computation; no file system or network access.
- **Method tool**: `graph.py` also decorates the method `NetworkGraph.shortest_path` (registered as `NetworkGraph.shortest_path`). It needs a `NetworkGraph` instance, so use it from Python rather than through MCP.

---

## Tool: `networks_analyze`

### 1. Tool Purpose and Description

Builds a network and returns node and edge counts, density, connected components and degree centrality.

### 2. Invocation Name

`networks_analyze`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `nodes` | `array[string]` | Yes | Node IDs | `["a", "b", "c"]` |
| `edges` | `array[array[string]]` | Yes | `[source, target]` pairs | `[["a", "b"]]` |

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "node_count": 3,
  "edge_count": 1,
  "density": 0.3333333333333333,
  "num_components": 2,
  "is_connected": false,
  "degree_centrality": {"a": 0.5, "b": 0.5, "c": 0.0}
}
```

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `networks_has_path`

### 1. Tool Purpose and Description

Builds a network and reports whether `target` is reachable from `source`.

### 2. Invocation Name

`networks_has_path`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `nodes` | `array[string]` | Yes | Node IDs | `["a", "b", "c"]` |
| `edges` | `array[array[string]]` | Yes | `[source, target]` pairs | `[["a", "b"]]` |
| `source` | `string` | Yes in practice | Source node ID (default `""`) | `"a"` |
| `target` | `string` | Yes in practice | Target node ID (default `""`) | `"c"` |

### 4. Output Schema (Return Value)

```json
{"status": "success", "has_path": false, "source": "a", "target": "c"}
```

An empty `source` or `target` returns `{"status": "error", "message": "source and target are required"}`.

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `networks_to_dict`

### 1. Tool Purpose and Description

Builds a network and returns its JSON-compatible serialisation.

### 2. Invocation Name

`networks_to_dict`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `name` | `string` | No | Network name (default `"default"`) | `"deps"` |
| `nodes` | `array[string]` | No | Node IDs (default none) | `["a", "b"]` |
| `edges` | `array[array[string]]` | No | `[source, target]` pairs (default none) | `[["a", "b"]]` |

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "network": {
    "name": "deps",
    "nodes": [
      {"id": "a", "data": null, "attributes": {}},
      {"id": "b", "data": null, "attributes": {}}
    ],
    "edges": [{"source": "a", "target": "b", "weight": 1.0, "attributes": {}}]
  }
}
```

### 5. Idempotency

- **Idempotent**: Yes

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
