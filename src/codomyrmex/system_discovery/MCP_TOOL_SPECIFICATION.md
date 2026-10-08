# system_discovery - MCP Tool Specification

## Overview

This document specifies the Model Context Protocol (MCP) tools provided by the `system_discovery` module. The tools are defined with the `@mcp_tool` decorator in `mcp_tools.py` and are surfaced by the PAI MCP bridge as `codomyrmex.<name>`.

| Tool | Purpose |
| :--- | :--- |
| `health_check` | Run a health check on the system or on one module |
| `list_modules` | List the importable Codomyrmex modules |
| `dependency_tree` | Report the public exports of one module |

## Tool Registration

Tools are defined with the `@mcp_tool` decorator in `mcp_tools.py` and are auto-discovered by the PAI MCP bridge; no manual registration call is needed. The decorated functions can also be called directly:

```python
from codomyrmex.system_discovery.mcp_tools import health_check, list_modules

modules = list_modules()
status = health_check()
```

## Related Documentation

- [Module README](./README.md)
- [API Specification](./API_SPECIFICATION.md)
- [Usage Examples](../README.md) (See README for examples)

---

## Tool: `health_check`

### 1. Tool Purpose and Description

Runs a health check on one module when `module` is given, otherwise on all modules, using `HealthChecker`.

**Known issue**: the implementation calls `HealthChecker.check_module()` and `HealthChecker.check_all()`, which `HealthChecker` does not define, so the tool currently returns the error shape below (for example `"'HealthChecker' object has no attribute 'check_all'"`).

### 2. Invocation Name

`health_check`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `module` | `string` or `null` | No | Module to check; all modules are checked when omitted | `"cache"` |

### 4. Output Schema (Return Value)

On success:

```json
{
  "status": "success",
  "healthy": true,
  "module": "all",
  "details": {}
}
```

`details` is the checker result's `to_dict()` output when available, otherwise its string form. On failure the tool returns `{"status": "error", "message": "<error>"}`.

## Tool: `list_modules`

### 1. Tool Purpose and Description

Lists the importable Codomyrmex packages reported by `codomyrmex.list_modules()`.

### 2. Invocation Name

`list_modules`

### 3. Input Schema (Parameters)

None.

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "modules": [
    {"name": "agentic_memory", "available": true},
    {"name": "agents", "available": true}
  ],
  "count": 2
}
```

On failure the tool returns `{"status": "error", "message": "<error>"}`.

## Tool: `dependency_tree`

### 1. Tool Purpose and Description

Imports `codomyrmex.<module>` and reports its public exports (`__all__`). Despite the name, it does not resolve dependencies between modules.

### 2. Invocation Name

`dependency_tree`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `module` | `string` | Yes | Module name to inspect (without the `codomyrmex.` prefix) | `"cache"` |

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "module": "cache",
  "exports": ["Cache", "CacheConnectionError", "CacheError"],
  "export_count": 3
}
```

When the module cannot be imported the tool returns `{"status": "error", "message": "Module not found: <module>", "detail": "<import error>"}`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
