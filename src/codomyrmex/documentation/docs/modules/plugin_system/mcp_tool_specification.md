# Plugin System - MCP Tool Specification

This document outlines the specification for tools within the Plugin System module that are integrated with the Model Context Protocol (MCP).

---

## Tool: `plugin_scan_entry_points`

### 1. Tool Purpose and Description

Scans installed Python packages for plugins registered under a given `importlib.metadata` entry point group. Returns the list of discovered plugins with their name, module path, and state.

### 2. Invocation Name

`plugin_scan_entry_points`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `entry_point_group` | `string` | No | Entry point group name to scan (default: `"codomyrmex.plugins"`) | `"codomyrmex.plugins"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` on success, `"error"` on failure | `"ok"` |
| `plugin_count` | `integer` | Total number of discovered plugins | `3` |
| `plugins` | `array[object]` | List of plugin descriptors | See below |
| `errors` | `array[object]` | List of `{"source": str, "error": str}` scan errors | `[]` |
| `error` | `string` | Top-level error message (only when `status == "error"`) | `"..."` |

**Plugin object structure:**

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `name` | `string` | Plugin name from entry point metadata |
| `module` | `string` | Importable module path (e.g. `"mypkg.plugin"`) |
| `state` | `string` | Discovery state value (e.g. `"discovered"`, `"error"`) |

### 5. Error Handling

- Returns `{"status": "error", "error": "<message>"}` if the scan itself fails
- Individual plugin load errors are collected in `errors` — scan continues

### 6. Idempotency

- **Idempotent**: Yes — reads installed package metadata, no side effects

### 7. Usage Examples

```json
{
  "tool_name": "plugin_scan_entry_points",
  "arguments": {
    "entry_point_group": "codomyrmex.plugins"
  }
}
```

**Example response:**
```json
{
  "status": "ok",
  "plugin_count": 2,
  "plugins": [
    {"name": "my-analyzer", "module": "mypkg.analyzer", "state": "discovered"},
    {"name": "my-formatter", "module": "mypkg.formatter", "state": "discovered"}
  ],
  "errors": []
}
```

### 8. Security Considerations

- **Read-Only**: Scans installed metadata, does not import or execute plugin code
- **Scope**: Only discovers plugins registered under the specified entry point group

---

## Tool: `plugin_resolve_dependencies`

### 1. Tool Purpose and Description

Resolves plugin dependencies using a topological sort and produces a valid load order. Detects missing dependencies and circular dependency cycles.

### 2. Invocation Name

`plugin_resolve_dependencies`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `plugins` | `array[object]` | Yes | List of plugin descriptor objects | See below |

**Plugin descriptor object:**

| Field Name | Type | Required | Description |
|:-----------|:-----|:---------|:------------|
| `name` | `string` | Yes | Unique plugin identifier |
| `dependencies` | `array[string]` | No | List of plugin names this plugin depends on (default: `[]`) |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` on success, `"error"` on failure | `"ok"` |
| `resolution_status` | `string` | Dependency resolution result (e.g. `"resolved"`, `"missing"`, `"circular"`) | `"resolved"` |
| `load_order` | `array[string]` | Plugin names in dependency-safe load order | `["base", "plugin-a", "plugin-b"]` |
| `missing` | `array[string]` | Plugin names referenced as dependencies but not in the input list | `[]` |
| `circular` | `array[string]` | Plugin names involved in circular dependency cycles | `[]` |
| `error` | `string` | Error message (only present when `status == "error"`) | `"..."` |

### 5. Error Handling

- Returns `{"status": "error", "error": "<message>"}` if resolution fails unexpectedly
- Missing and circular dependency issues are reported in `missing` / `circular` fields, not as errors

### 6. Idempotency

- **Idempotent**: Yes — pure computation over the input graph

### 7. Usage Examples

```json
{
  "tool_name": "plugin_resolve_dependencies",
  "arguments": {
    "plugins": [
      {"name": "plugin-b", "dependencies": ["plugin-a"]},
      {"name": "plugin-a", "dependencies": []},
      {"name": "plugin-c", "dependencies": ["plugin-a", "plugin-b"]}
    ]
  }
}
```

**Example response:**
```json
{
  "status": "ok",
  "resolution_status": "resolved",
  "load_order": ["plugin-a", "plugin-b", "plugin-c"],
  "missing": [],
  "circular": []
}
```

### 8. Security Considerations

- **No Code Execution**: Performs graph analysis only — no plugin code is imported or run
- **Input Validation**: Malformed plugin names or dependency lists return structured errors

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
