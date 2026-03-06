# Codomyrmex Modules -- Technical Specification Overview

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document provides the top-level technical specification for the codomyrmex module system. Each module subdirectory contains its own `SPEC.md` with detailed functional requirements, interface contracts, and non-functional requirements.

## System Architecture

### Layered Dependency Model

Dependencies flow upward only. No module may depend on a module in a higher layer.

```
+-------------------+
| Application Layer | -- CLI, audio, video, domain modules
+-------------------+
| Service Layer     | -- CI/CD, containerization, orchestration, email
+-------------------+
| Core Layer        | -- agents, coding, git_operations, llm, cache
+-------------------+
| Foundation Layer  | -- logging, environment_setup, MCP, terminal, utils
+-------------------+
```

### Module Discovery

- Auto-discovery via `pkgutil` scan of all `mcp_tools.py` submodules
- `@mcp_tool` decorator registers tools with 5-minute TTL cache
- 141 modules currently auto-discovered, ~474 total MCP tools
- Discovery entry point: `src/codomyrmex/agents/pai/mcp/discovery.py`

## Cross-Cutting Requirements

### NFR-1: Zero-Mock Policy

All modules shall follow the zero-mock testing policy:

- No `unittest.mock`, `MagicMock`, `monkeypatch`, or `pytest-mock`
- External dependencies use `@pytest.mark.skipif` guards
- Production code never returns placeholder data
- Unimplemented features raise `NotImplementedError`

### NFR-2: No Silent Fallbacks

- Fallback patterns that silently degrade functionality are prohibited
- All failures must be explicit and logged
- Error propagation uses exception chaining (`raise ... from ...`)

### NFR-3: Trust Gateway

- All MCP tool invocations pass through the Trust Gateway
- Destructive tools require explicit trust elevation
- Trust state persists to `~/.codomyrmex/trust_ledger.json`
- Three levels: UNTRUSTED, VERIFIED, TRUSTED

### NFR-4: Configuration

- No hardcoded URLs, ports, or connection strings
- All configurable values use `os.getenv()` with centralized defaults
- Module-specific configuration via `config_management` module

### NFR-5: Lazy Loading

- Modules load on demand to minimize startup time
- Heavy optional dependencies (cloud SDKs, ML frameworks) are conditionally imported
- `ImportError` is caught and availability flags are set

### NFR-6: RASP Documentation

Every module shall maintain four documentation files:

| File | Purpose |
|------|---------|
| `README.md` | Human-readable module overview |
| `AGENTS.md` | Agent integration guide with MCP tool tables |
| `SPEC.md` | Technical specification with interface contracts |
| `PAI.md` | PAI phase mapping and AI capability description |

### NFR-7: Test Markers

Tests shall use standardized pytest markers:

- `@pytest.mark.unit` -- Unit tests
- `@pytest.mark.integration` -- Integration tests
- `@pytest.mark.slow` -- Long-running tests
- `@pytest.mark.network` -- Tests requiring network access
- `@pytest.mark.external` -- Tests requiring external services

## Interface Standards

### MCP Tool Interface

All MCP tools shall follow this signature pattern:

```python
@mcp_tool(
    name="module_action",
    description="Clear description of what this tool does",
    schema={
        "type": "object",
        "properties": {
            "param_name": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param_name"]
    }
)
def tool_function(param_name: str) -> dict:
    """Tool implementation."""
    return {"status": "success", "data": result}
```

### Return Value Contract

MCP tools shall return dictionaries with:

- `"status"`: Either `"success"` or `"error"`
- `"data"` or `"message"`: Result payload or error description
- Additional keys as needed by the specific tool

### Error Handling Contract

Modules shall:

- Define module-specific exception classes inheriting from a base exception
- Use structured logging via `logging_monitoring`
- Propagate errors with exception chaining (`raise X from Y`)
- Never silently swallow exceptions

## Module Inventory by Layer

### Foundation (6 modules)

| Module | Key Interfaces | Spec |
|--------|---------------|------|
| environment_setup | `check_dependencies()`, `validate_env()` | [SPEC](environment_setup/SPEC.md) |
| exceptions | Base exception hierarchy | [SPEC](exceptions/SPEC.md) |
| logging_monitoring | `logging_format_structured()` | [SPEC](logging_monitoring/SPEC.md) |
| model_context_protocol | `inspect_server()`, `list_registered_tools()` | [SPEC](model_context_protocol/SPEC.md) |
| terminal_interface | Rich terminal output | [SPEC](terminal_interface/SPEC.md) |
| utils | Shared utilities | [SPEC](utils/SPEC.md) |

### Core (20 modules)

| Module | Key Interfaces | Spec |
|--------|---------------|------|
| agents | `execute_agent()`, `list_agents()` | [SPEC](agents/SPEC.md) |
| agentic_memory | `memory_put()`, `memory_get()`, `memory_search()` | [SPEC](agentic_memory/SPEC.md) |
| auth | Token validation, permission checking | [SPEC](auth/SPEC.md) |
| cache | `cache_get()`, `cache_set()`, `cache_delete()` | [SPEC](cache/SPEC.md) |
| cerebrum | `query_knowledge_base()`, `add_case_reference()` | [SPEC](cerebrum/SPEC.md) |
| coding | `code_execute()`, `code_review_file()` | [SPEC](coding/SPEC.md) |
| collaboration | `swarm_submit_task()`, `pool_status()` | [SPEC](collaboration/SPEC.md) |
| compression | `compress()`, `decompress()` | [SPEC](compression/SPEC.md) |
| concurrency | Thread/process pool management | [SPEC](concurrency/SPEC.md) |
| config_management | `get_config()`, `set_config()` | [SPEC](config_management/SPEC.md) |
| crypto | `hash_data()`, `verify_hash()`, `generate_key()` | [SPEC](crypto/SPEC.md) |
| encryption | Symmetric/asymmetric encryption | [SPEC](encryption/SPEC.md) |
| events | `emit_event()`, `list_event_types()` | [SPEC](events/SPEC.md) |
| git_operations | 35 git automation tools | [SPEC](git_operations/SPEC.md) |
| llm | `generate_text()`, `list_local_models()` | [SPEC](llm/SPEC.md) |
| networking | HTTP client utilities | [SPEC](networking/SPEC.md) |
| search | `search_documents()`, `search_fuzzy()` | [SPEC](search/SPEC.md) |
| serialization | JSON/YAML/MessagePack | [SPEC](serialization/SPEC.md) |
| static_analysis | Code quality scanning | [SPEC](static_analysis/SPEC.md) |
| validation | `validate_schema()`, `validate_config()` | [SPEC](validation/SPEC.md) |

### Service (29 modules)

See individual module `SPEC.md` files for detailed interface contracts.

### Application (22 modules)

See individual module `SPEC.md` files for detailed interface contracts.

## Performance Requirements

- Module import time: < 100ms per module (lazy loading)
- MCP tool discovery: < 5s for full scan (cached for 5 minutes)
- MCP tool response: < 30s for non-streaming tools
- Test suite: < 10 minutes for full run (excluding `@pytest.mark.slow`)

## Navigation

- **Module index**: [README.md](README.md)
- **Agent integration**: [AGENTS.md](AGENTS.md)
- **Source modules**: [src/codomyrmex/](../../../src/codomyrmex/)
