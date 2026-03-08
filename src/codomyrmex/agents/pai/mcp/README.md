# PAI MCP Bridge

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

MCP bridge subpackage that implements the complete Codomyrmex-to-PAI tool surface. It defines 20 static tools as typed tuples, auto-discovers ~300 dynamic module tools via `@mcp_tool` decorator scanning, registers 3 MCP resources and 10 prompts, and provides both a full MCP server assembly path and a direct Python `call_tool()` entry point with trust enforcement through the trust gateway.

This subpackage was decomposed from the original monolithic `mcp_bridge.py` into four focused modules for maintainability.

## PAI Integration

| Algorithm Phase | Role |
|----------------|------|
| OBSERVE | `list_modules`, `module_info`, `list_directory` -- discover available capabilities |
| THINK | `analyze_python`, `search_codebase` -- analyze code structure and patterns |
| PLAN | `read_file`, `json_query` -- read configuration and specifications |
| BUILD | `write_file` -- create and modify source files |
| EXECUTE | `run_command`, `run_tests` -- execute shell commands and test suites |
| VERIFY | `git_status`, `git_diff`, `checksum_file` -- verify changes and integrity |
| LEARN | `pai_awareness`, `pai_status` -- retrieve PAI state for learning |

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `TOOL_DEFINITIONS` | `list[tuple]` | 20 static tool tuples: (name, description, handler, input_schema) |
| `RESOURCE_DEFINITIONS` | `list[tuple]` | 2 MCP resource definitions (modules inventory, system status) |
| `PROMPT_DEFINITIONS` | `list[tuple]` | 10 MCP prompt templates for common workflows |
| `discover_dynamic_tools` | `function` | TTL-cached scan of all `mcp_tools.py` submodules via `pkgutil` |
| `invalidate_tool_cache` | `function` | Clear the dynamic tool discovery cache |
| `get_tool_registry` | `function` | Build a registry populated with all static + dynamic tools |
| `create_codomyrmex_mcp_server` | `function` | Assemble a fully-configured MCPServer instance |
| `call_tool` | `function` | Direct Python tool invocation with trust enforcement |
| `get_skill_manifest` | `function` | PAI-compatible skill manifest with tools, resources, and algorithm mapping |

## Quick Start

```python
from codomyrmex.agents.pai.mcp.server import call_tool, get_tool_registry

# Direct tool invocation (goes through trust gateway)
result = call_tool("codomyrmex.list_modules")

# Build a full registry for inspection
registry = get_tool_registry()
print(f"Total tools: {len(registry.list_tools())}")

# Create and run a standalone MCP server
from codomyrmex.agents.pai.mcp.server import create_codomyrmex_mcp_server
server = create_codomyrmex_mcp_server(transport="stdio")
```

## Architecture

```
pai/mcp/
├── __init__.py        # Package marker ("Codomyrmex MCP bridge submodules")
├── definitions.py     # Static TOOL/RESOURCE/PROMPT definitions as typed tuples
├── discovery.py       # TTL-cached dynamic tool scanner using pkgutil + MCPDiscovery
├── proxy_tools.py     # Handler implementations for core proxy tools
├── server.py          # _ToolRegistry, server assembly, call_tool, skill manifest
├── AGENTS.md          # Agent coordination documentation
├── README.md          # This file
└── SPEC.md            # Technical specification
```

### Module Responsibilities

| File | Primary Role |
|------|-------------|
| `definitions.py` | Single source of truth for 20 static tools, 2 resources, 10 prompts |
| `discovery.py` | Thread-safe, TTL-cached auto-discovery of `@mcp_tool` decorators across 87+ modules |
| `proxy_tools.py` | 9 handler functions: module listing, introspection, PAI status, test runner, workflow listing |
| `server.py` | `_ToolRegistry` class, `create_codomyrmex_mcp_server()`, `call_tool()`, `get_skill_manifest()` |

## Static Tool Categories

| Category | Tools | Count |
|----------|-------|-------|
| File Operations | `read_file`, `write_file`, `list_directory` | 3 |
| Code Analysis | `analyze_python`, `search_codebase` | 2 |
| Git Operations | `git_status`, `git_diff` | 2 |
| Shell | `run_command` | 1 |
| Data Utilities | `json_query`, `checksum_file` | 2 |
| Discovery | `list_modules`, `module_info` | 2 |
| PAI | `pai_status`, `pai_awareness` | 2 |
| Testing | `run_tests` | 1 |
| Universal Proxy | `list_module_functions`, `call_module_function`, `get_module_readme` | 3 |
| Maintenance | `invalidate_cache`, `list_workflows` | 2 |

## MCP Resources

| URI | Name | Description |
|-----|------|-------------|
| `codomyrmex://modules` | Module Inventory | Complete list of all Codomyrmex modules |
| `codomyrmex://status` | System Status | Current system status including PAI integration |
| `codomyrmex://discovery/metrics` | Discovery Metrics | Runtime metrics from tool discovery (scan time, failures, cache hits) |

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `CODOMYRMEX_MCP_CACHE_TTL` | `300` | Dynamic tool discovery cache TTL in seconds |

## Dependencies

**Internal**: `codomyrmex.logging_monitoring`, `codomyrmex.model_context_protocol.tools`, `codomyrmex.model_context_protocol.transport.server`, `codomyrmex.model_context_protocol.discovery`, `codomyrmex.model_context_protocol.errors`, `codomyrmex.agents.pai.trust_gateway`, `codomyrmex.website.data_provider`

**External**: `yaml` (workflow frontmatter parsing), standard library (`importlib`, `inspect`, `subprocess`, `pkgutil`, `threading`, `time`, `json`, `pathlib`)

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [Parent](../README.md)
