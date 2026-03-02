# Codomyrmex Agents — src/codomyrmex/model_context_protocol/discovery

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Auto-discovers MCP tools and servers at runtime by scanning Python packages for functions decorated with `@mcp_tool`. Builds and maintains an in-memory registry of `DiscoveredTool` instances, supporting error-isolated scanning (a broken module never kills the full scan), incremental single-module refresh, tag-based filtering, and runtime discovery metrics.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `MCPDiscovery` | Main discovery engine; scans packages via `pkgutil.walk_packages`, builds registry of `DiscoveredTool` instances |
| `__init__.py` | `DiscoveredTool` | Dataclass representing a discovered tool with name, parameters, tags, version, availability status, and handler reference |
| `__init__.py` | `DiscoveredServer` | Dataclass grouping tools and resources under a named MCP server |
| `__init__.py` | `FailedModule` | Records modules that failed to import during scanning (module name, error, error type) |
| `__init__.py` | `DiscoveryReport` | Result container for a scan: discovered tools, failed modules, timing, and module count |
| `__init__.py` | `DiscoveryMetrics` | Runtime metrics: total tools, scan duration, cache hits, failed modules, last scan time |
| `__init__.py` | `mcp_tool()` | Decorator that attaches `_mcp_tool_meta` to functions, auto-generating JSON Schema from type annotations via `_generate_schema_from_func` |

## Operating Contracts

- Each sub-module is imported inside its own `try/except` block so that a broken module never prevents other tools from being discovered.
- `scan_module()` merges new tools into the existing registry without clearing previously discovered tools (incremental refresh).
- Tools missing required dependencies (checked via `importlib.util.find_spec`) are registered as `available=False` with an `unavailable_reason`.
- The `mcp_tool` decorator imports `_generate_schema_from_func` from `quality.validation` to build input schemas at decoration time.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.model_context_protocol.quality.validation` (schema generation at decoration time)
- **Used by**: `codomyrmex.agents.pai.mcp_bridge` (PAI MCP bridge uses discovery to find all `@mcp_tool` decorated functions), `model_context_protocol.transport.main` (server startup scans for tools)

## Navigation

- **Parent**: [model_context_protocol](../README.md)
- **Root**: [Root](../../../../README.md)
