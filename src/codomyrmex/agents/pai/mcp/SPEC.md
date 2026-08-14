# PAI MCP Bridge — Technical Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: August 2026

## Overview

Core MCP bridge subpackage that assembles the full Codomyrmex tool surface for PAI consumption. Defines 20 static tools, auto-discovers ~150 dynamic module tools via `@mcp_tool` scanning, registers 2 resources and 10 prompts, and provides both MCP server assembly and direct Python call paths with trust enforcement.

## Architecture

Four-file decomposition of the original monolithic `mcp_bridge.py`:

1. **definitions.py**: Static tool/resource/prompt definitions as typed tuples. Single source of truth for the 20 core tools.
2. **discovery.py**: TTL-cached dynamic tool scanner using `pkgutil.walk_packages` + `MCPDiscovery` engine. Thread-safe cache with configurable expiry.
3. **proxy_tools.py**: Handler implementations for core tools (module introspection, PAI status, test runner, workflow listing).
4. **server.py**: `_ToolRegistry` + `create_codomyrmex_mcp_server()` + `call_tool()` + `get_skill_manifest()`. Wires everything together.
5. **path_policy.py**: Capability-root enforcement for path-like arguments at the PAI/MCP boundary. The current working tree is the default root; `CODOMYRMEX_MCP_ALLOWED_ROOTS` adds explicit roots.

## Key Classes and Functions

### `_ToolRegistry` (server.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register` | `tool_name`, `schema`, `handler` | `None` | Register a tool with its schema and handler; static first registration wins on collisions |
| `list_tools` | — | `list[str]` | Sorted list of all registered tool names |
| `get` | `name: str` | `dict or None` | Lookup a defensive copy of a tool entry |

### `get_tool_registry()` (server.py)

Returns a fully-populated `_ToolRegistry` with all static tools from `TOOL_DEFINITIONS` and all dynamically discovered module tools.
The cache is invalidated atomically when discovery changes, and callers cannot mutate the cached schemas through `get()`.

### `create_codomyrmex_mcp_server()` (server.py)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | `"codomyrmex-mcp-server"` | Server identity |
| `transport` | `str` | `"stdio"` | Transport mode: stdio or http |

Registers all tools, 2 static resources + 1 discovery metrics resource, and 10 prompts onto an `MCPServer` instance.

### `call_tool()` (server.py)

Direct Python tool invocation that delegates to `trust_gateway.trusted_call_tool()`. Wraps errors into structured `MCPToolError` dicts with appropriate error codes (ACCESS_DENIED, TIMEOUT, validation_error, execution_error).

### `discover_dynamic_tools()` (discovery.py)

Thread-safe, TTL-cached discovery. Uses `_find_mcp_modules()` to locate all packages with `mcp_tools` submodules, then delegates to `MCPDiscovery.scan_package()` for `@mcp_tool` extraction.

## Static Tool Categories

| Category | Tools | Count |
|----------|-------|-------|
| File Operations | read_file, write_file, list_directory | 3 |
| Code Analysis | analyze_python, search_codebase | 2 |
| Git Operations | git_status, git_diff | 2 |
| Shell | run_command | 1 |
| Data Utilities | json_query, checksum_file | 2 |
| Discovery | list_modules, module_info | 2 |
| PAI | pai_status, pai_awareness | 2 |
| Testing | run_tests | 1 |
| Universal Proxy | list_module_functions, call_module_function, get_module_readme | 3 |
| Cache | invalidate_cache, list_workflows | 2 |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring`, `codomyrmex.model_context_protocol.tools`, `codomyrmex.model_context_protocol.transport.server`, `codomyrmex.model_context_protocol.discovery`, `codomyrmex.model_context_protocol.errors`, `codomyrmex.model_context_protocol.quality.validation`, `codomyrmex.agents.pai.trust_gateway`, `codomyrmex.website.data_provider`
- **External**: `yaml` (for workflow frontmatter parsing), standard library (`importlib`, `inspect`, `subprocess`, `pkgutil`, `threading`, `time`, `json`, `pathlib`)

## Constraints

- Cache TTL defaults to 300 seconds; configurable via `CODOMYRMEX_MCP_CACHE_TTL` environment variable.
- Path-bearing arguments are resolved and constrained to configured capability roots before dispatch, including dynamically discovered tools with `path`, `cwd`, `directory`, `*_path`, `*_dir`, or related fields.
- Trust ledger signatures use a randomly generated owner-only key at `~/.codomyrmex/trust_ledger.key` (or `CODOMYRMEX_TRUST_KEY_PATH`); public machine identifiers are never used as signing secrets.
- `tool_call_module_function` blocks private function calls (names starting with `_`) and non-callable attributes.
- `tool_run_tests` enforces a 120-second subprocess timeout.
- Zero-mock: all tools perform real operations; `NotImplementedError` for unimplemented paths.

## Error Handling

- `call_tool()` catches `KeyError` (unknown tool), `SecurityError` (trust violation), `ValueError` (validation failure), `TimeoutError`, and generic `Exception`, returning structured error dicts.
- Trust failures are surfaced as `ACCESS_DENIED`, not generic execution failures. Confirmation digests bind the authorization to the exact JSON arguments.
- Proxy tools return `{"error": ...}` dicts rather than raising, ensuring MCP protocol compatibility.
- Discovery failures for individual modules are logged and skipped; overall discovery continues.

## Navigation

- **Self**: `SPEC.md`
- **Parent**: [../README.md](../README.md)
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [README.md](../../../../../README.md)
