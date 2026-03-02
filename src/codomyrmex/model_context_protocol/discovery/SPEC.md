# Discovery — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Runtime auto-discovery engine for MCP tools and servers. Scans Python packages for `@mcp_tool`-decorated functions, builds an in-memory registry with error isolation, incremental refresh, and runtime metrics.

## Architecture

Uses `pkgutil.walk_packages` with per-module `try/except` isolation. Each discovered function's `_mcp_tool_meta` attribute (set by the `@mcp_tool` decorator) is inspected to extract name, description, parameters, tags, version, and dependency requirements. Tools with missing dependencies are registered as unavailable rather than silently dropped.

## Key Classes

### `MCPDiscovery`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `scan_package` | `package_name: str` | `DiscoveryReport` | Walk all sub-modules of a package, discover tools with error isolation |
| `scan_module` | `module_name: str` | `DiscoveryReport` | Scan a single module and merge into existing registry (incremental) |
| `register_tool` | `tool: DiscoveredTool` | `None` | Manually register a tool |
| `get_tool` | `name: str` | `DiscoveredTool | None` | Look up a tool by name |
| `list_tools` | `tag: str | None` | `list[DiscoveredTool]` | List all tools, optionally filtered by tag |
| `record_cache_hit` | — | `None` | Increment cache-hit counter |
| `get_metrics` | — | `DiscoveryMetrics` | Return current scan and registry metrics |

### `DiscoveredTool`

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Tool identifier |
| `description` | `str` | Human-readable description |
| `module_path` | `str` | Fully-qualified module containing the tool |
| `callable_name` | `str` | Function name within the module |
| `parameters` | `dict[str, Any]` | JSON Schema for tool input |
| `tags` | `list[str]` | Classification tags |
| `version` | `str` | Semantic version |
| `requires` | `list[str]` | Required importable packages |
| `available` | `bool` | Whether all dependencies are present |
| `handler` | `Callable | None` | Reference to the actual function |

### `mcp_tool()` decorator

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str | None` | Override tool name (default: function name) |
| `description` | `str` | Tool description (default: docstring) |
| `tags` | `list[str] | None` | Classification tags |
| `version` | `str` | Semantic version string |
| `requires` | `list[str] | None` | Required packages; missing ones mark tool unavailable |

## Dependencies

- **Internal**: `codomyrmex.model_context_protocol.quality.validation` (`_generate_schema_from_func`)
- **External**: Standard library only (`importlib`, `pkgutil`, `inspect`, `time`, `dataclasses`)

## Constraints

- Scanning never raises on import errors; failures are captured in `FailedModule` records within the `DiscoveryReport`.
- `scan_module` is additive: it merges into the existing registry without clearing other tools.
- Zero-mock: real package introspection only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `ImportError` during root package import returns a `DiscoveryReport` with a single `FailedModule` entry.
- Per-module exceptions during `scan_package` are caught, logged at debug level, and appended to `failed_modules`.
- All errors logged before propagation.
