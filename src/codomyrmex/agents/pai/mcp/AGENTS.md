# Codomyrmex Agents — src/codomyrmex/agents/pai/mcp

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

MCP bridge subpackage that implements the full Codomyrmex-to-PAI tool surface: static tool definitions, dynamic tool auto-discovery via `@mcp_tool` scanning, proxy tool handlers for module introspection and execution, and MCP server assembly with resource and prompt registration.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `definitions.py` | `_TOOL_DEFINITIONS` | 22 static tool tuples: (name, description, handler, input_schema) covering file ops, code analysis, git, shell, discovery, PAI, testing, universal proxy, and maintenance |
| `definitions.py` | `_RESOURCE_DEFINITIONS` | 2 MCP resources: `codomyrmex://modules` and `codomyrmex://status` |
| `definitions.py` | `_PROMPT_DEFINITIONS` | 10 MCP prompts: analyze_module, debug_issue, create_test, codomyrmexAnalyze/Memory/Search/Docs/Status/Verify/Trust |
| `discovery.py` | `_discover_dynamic_tools` | TTL-cached scan of all `mcp_tools.py` submodules via `pkgutil.walk_packages`, delegating to `MCPDiscovery` engine |
| `discovery.py` | `invalidate_tool_cache` | Clear the dynamic tool cache and its TTL |
| `discovery.py` | `_find_mcp_modules` | Auto-discover codomyrmex packages containing `mcp_tools` submodules; falls back to 8 hardcoded targets |
| `proxy_tools.py` | `_tool_list_modules` | List all Codomyrmex modules |
| `proxy_tools.py` | `_tool_module_info` | Introspect a module's docstring, exports, and path |
| `proxy_tools.py` | `_tool_list_module_functions` | List public functions and classes in any module |
| `proxy_tools.py` | `_tool_call_module_function` | Execute any public function by dotted path (destructive tool) |
| `proxy_tools.py` | `_tool_pai_status` / `_tool_pai_awareness` | PAI installation status and full awareness data |
| `proxy_tools.py` | `_tool_run_tests` | Run pytest for a module or whole project |
| `proxy_tools.py` | `_tool_list_workflows` | Parse YAML frontmatter from `.agent/workflows/*.md` |
| `server.py` | `_ToolRegistry` | Lightweight in-process tool registry replacing MCP SDK's MCPToolRegistry |
| `server.py` | `get_tool_registry` | Build registry with all static + dynamically discovered tools |
| `server.py` | `create_codomyrmex_mcp_server` | Assemble MCPServer with tools, resources, prompts, and discovery metrics |
| `server.py` | `call_tool` | Direct Python tool invocation with trust enforcement via `trusted_call_tool` |
| `server.py` | `get_skill_manifest` | PAI-compatible manifest with tools, resources, workflows, algorithm mapping |

## Operating Contracts

- Dynamic tool discovery uses a 300-second TTL cache (configurable via `CODOMYRMEX_MCP_CACHE_TTL` env var). `invalidate_tool_cache()` forces rescan.
- `_find_mcp_modules()` walks the entire `codomyrmex` package tree via `pkgutil.walk_packages`; falls back to `_FALLBACK_SCAN_TARGETS` if walk fails.
- `call_tool()` delegates to `trust_gateway.trusted_call_tool()` for authorization, audit logging, and destructive action confirmation.
- `_tool_call_module_function` blocks calls to private functions (names starting with `_`).
- `_tool_run_tests` enforces a 120-second subprocess timeout.
- Proxy tools return structured dicts with `error` keys on failure rather than raising exceptions.
- All handlers log via `logging_monitoring.get_logger()`.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring`, `codomyrmex.model_context_protocol.tools`, `codomyrmex.model_context_protocol.transport.server`, `codomyrmex.model_context_protocol.discovery`, `codomyrmex.model_context_protocol.errors`, `codomyrmex.agents.pai.trust_gateway`
- **Used by**: `agents/pai/__init__.py` (re-exports), `agents/pai/trust_gateway.py` (registry access), PAI skill routing

## Navigation

- **Parent**: [pai](../README.md)
- **Root**: [Root](../../../../../README.md)
