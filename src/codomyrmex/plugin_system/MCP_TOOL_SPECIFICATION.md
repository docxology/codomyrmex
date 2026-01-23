# Plugin System - MCP Tool Specification

This document outlines the specification for tools within the Plugin System module that are intended to be integrated with the Model Context Protocol (MCP).

## General Considerations

- **Tool Integration**: This module provides plugin architecture for extending Codomyrmex functionality.
- **Configuration**: Plugins are discovered from configured directories and can have their own configurations.

---

## Tool: `list_plugins`

### 1. Tool Purpose and Description

Lists all available plugins with their metadata, status, and capabilities.

### 2. Invocation Name

`list_plugins`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `plugin_type` | `string` | No | Filter by plugin type | `"analyzer"` |
| `status` | `string` | No | Filter by status ("active", "disabled", "error") | `"active"` |
| `include_disabled` | `boolean` | No | Include disabled plugins (default: true) | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `plugins` | `array[object]` | List of plugin information | See below |
| `total_count` | `integer` | Total number of plugins | `12` |
| `active_count` | `integer` | Number of active plugins | `10` |

**Plugin object structure:**

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `name` | `string` | Plugin identifier |
| `version` | `string` | Plugin version |
| `description` | `string` | Plugin description |
| `plugin_type` | `string` | Type (analyzer, formatter, exporter, etc.) |
| `status` | `string` | Current status |
| `dependencies` | `array[string]` | Required dependencies |
| `author` | `string` | Plugin author |

### 5. Error Handling

- Returns empty list if no plugins are available

### 6. Idempotency

- **Idempotent**: Yes

### 7. Usage Examples

```json
{
  "tool_name": "list_plugins",
  "arguments": {
    "plugin_type": "analyzer",
    "status": "active"
  }
}
```

### 8. Security Considerations

- **Plugin Verification**: Plugins should be verified before installation
- **Sandbox Execution**: Consider sandboxing plugin code execution

---

## Tool: `load_plugin`

### 1. Tool Purpose and Description

Loads and activates a plugin by name or path.

### 2. Invocation Name

`load_plugin`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `plugin_name` | `string` | Yes | Name or path of the plugin | `"my-analyzer"` |
| `config` | `object` | No | Configuration to pass to the plugin | `{"verbose": true}` |
| `validate_only` | `boolean` | No | Validate without loading | `false` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | "loaded", "validated", or "error" | `"loaded"` |
| `plugin_info` | `object` | Plugin metadata after loading | See plugin object |
| `validation_errors` | `array[string]` | Validation issues if any | `[]` |
| `warning_messages` | `array[string]` | Non-critical warnings | `["Deprecated API used"]` |

### 5. Error Handling

- **Plugin Not Found**: Returns error if plugin cannot be located
- **Dependency Missing**: Returns error with missing dependencies list
- **Security Violation**: Returns error if plugin fails security scan
- **Load Error**: Returns error with details if plugin fails to initialize

### 6. Idempotency

- **Idempotent**: Yes, loading an already-loaded plugin returns success

---

## Tool: `unload_plugin`

### 1. Tool Purpose and Description

Unloads and deactivates a currently loaded plugin.

### 2. Invocation Name

`unload_plugin`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `plugin_name` | `string` | Yes | Name of the plugin to unload | `"my-analyzer"` |
| `force` | `boolean` | No | Force unload even if in use | `false` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `status` | `string` | "unloaded" or "error" |
| `cleanup_performed` | `boolean` | Whether cleanup hooks were called |

### 5. Error Handling

- **Plugin Not Loaded**: Returns error if plugin is not currently loaded
- **In Use**: Returns error if plugin is in use and force is false

### 6. Idempotency

- **Idempotent**: Yes

---

## Tool: `execute_plugin_hook`

### 1. Tool Purpose and Description

Executes a registered hook across all plugins that implement it.

### 2. Invocation Name

`execute_plugin_hook`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `hook_name` | `string` | Yes | Name of the hook to execute | `"pre_analysis"` |
| `arguments` | `object` | No | Arguments to pass to hook handlers | `{"file_path": "..."}` |
| `plugin_filter` | `array[string]` | No | Only execute for specific plugins | `["plugin-a"]` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `status` | `string` | "success", "partial", or "error" |
| `results` | `array[object]` | Results from each plugin |
| `errors` | `array[object]` | Errors from failed handlers |

### 5. Error Handling

- **Hook Not Found**: Returns info if no plugins implement the hook
- **Handler Errors**: Continues execution, collects all errors

### 6. Idempotency

- **Idempotent**: Depends on hook implementation

---

## Tool: `get_plugin_status`

### 1. Tool Purpose and Description

Gets detailed status information for a specific plugin.

### 2. Invocation Name

`get_plugin_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `plugin_name` | `string` | Yes | Name of the plugin | `"my-analyzer"` |
| `include_metrics` | `boolean` | No | Include usage metrics | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `plugin_info` | `object` | Full plugin metadata |
| `state` | `string` | Current state (loaded, active, disabled, error) |
| `config` | `object` | Current configuration |
| `metrics` | `object` | Usage metrics (if requested) |
| `last_error` | `string` | Last error message if any |

### 5. Error Handling

- **Plugin Not Found**: Returns error if plugin doesn't exist

### 6. Idempotency

- **Idempotent**: Yes

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
