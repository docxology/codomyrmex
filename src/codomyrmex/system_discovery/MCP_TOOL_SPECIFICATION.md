# system_discovery - MCP Tool Specification

## Overview

This document specifies the Model Context Protocol (MCP) tools provided by the `system_discovery` module.

## Available Tools

### `tool_name`

**Description**: [Tool description]

**Parameters**:
```json
{
  "param1": {
    "type": "string",
    "description": "Parameter description",
    "required": true
  },
  "param2": {
    "type": "integer",
    "description": "Parameter description",
    "required": false,
    "default": 0
  }
}
```

**Returns**: Return value description

**Example**:
```json
{
  "tool": "tool_name",
  "parameters": {
    "param1": "value",
    "param2": 42
  }
}
```

## Tool Registration

Tools are automatically registered when the module is imported:

```python
from codomyrmex.system_discovery import register_tools

register_tools()
```

## Related Documentation

- [Module README](./README.md)
- [API Specification](./API_SPECIFICATION.md)
- [Usage Examples](../README.md#usage-examples) (See README for examples)

---

## Tool: `discover_system_capabilities`

### 1. Tool Purpose and Description

Discovers and catalogs system capabilities, installed modules, and available resources within the Codomyrmex ecosystem.

### 2. Invocation Name

`discover_system_capabilities`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `scan_depth` | `string` | No | Depth of discovery scan (basic, detailed, full) | `"detailed"` |
| `include_modules` | `boolean` | No | Whether to scan individual modules for capabilities | `true` |
| `include_resources` | `boolean` | No | Whether to scan system resources | `true` |
| `output_format` | `string` | No | Output format (json, text, summary) | `"json"` |

### 4. Output Schema (Return Value)

```json
{
  "capabilities": {
    "modules": ["ai_code_editing", "static_analysis", "data_visualization"],
    "resources": {
      "cpu_cores": 8,
      "memory_gb": 16,
      "storage_gb": 256
    },
    "integrations": ["ollama", "docker", "kubernetes"]
  },
  "system_info": {
    "platform": "macOS",
    "python_version": "3.10.5",
    "codomyrmex_version": "0.1.0"
  },
  "scan_timestamp": "2025-01-18T13:46:57.230Z"
}
```

## Tool: `get_system_status`

### 1. Tool Purpose and Description

Retrieves system status including health metrics, active processes, and system utilization.

### 2. Invocation Name

`get_system_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `include_health` | `boolean` | No | Include system health metrics | `true` |
| `include_processes` | `boolean` | No | Include running process information | `false` |
| `include_modules` | `boolean` | No | Include module status information | `true` |

### 4. Output Schema (Return Value)

```json
{
  "health_status": "healthy",
  "system_metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 68.1,
    "disk_usage": 23.4
  },
  "module_status": {
    "active_modules": 27,
    "healthy_modules": 26,
    "warnings": 1
  },
  "timestamp": "2025-01-18T13:46:57.230Z"
}
```

## Tool: `scan_module_capabilities`

### 1. Tool Purpose and Description

Scans specific modules for their capabilities, exported functions, and integration points.

### 2. Invocation Name

`scan_module_capabilities`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `module_name` | `string` | Yes | Name of the module to scan | `"ai_code_editing"` |
| `include_functions` | `boolean` | No | Include exported function signatures | `true` |
| `include_dependencies` | `boolean` | No | Include module dependencies | `true` |

### 4. Output Schema (Return Value)

```json
{
  "module_name": "ai_code_editing",
  "capabilities": {
    "functions": [
      "generate_code_snippet",
      "refactor_code_snippet",
      "analyze_code_quality"
    ],
    "languages": ["python", "javascript", "java", "cpp"],
    "providers": ["openai", "anthropic", "google"]
  },
  "dependencies": ["language_models", "pattern_matching"],
  "mcp_tools": ["generate_code_snippet", "refactor_code_snippet"]
}
```

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
