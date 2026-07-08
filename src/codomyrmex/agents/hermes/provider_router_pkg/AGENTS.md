# provider_router_pkg/ — AGENTS.md

## Purpose

Provider routing, context compression, and MCP bridge (split from `_provider_router.py`).

## Key Files

| Module | Type | Responsibility |
| --- | --- | --- |
| `router.py` | `ProviderRouter` | Unified `call_llm()` dispatch |
| `user_model.py` | `UserModel` | Cross-session user modeling |
| `context_registry.py` | `ModelContextRegistry`, `get_model_context_registry()` | Dynamic context window lookup |
| `compressor.py` | `ContextCompressor` | Token overflow compression |
| `mcp_bridge.py` | `MCPBridgeManager` | MCP server hot-reload |

## Dependencies

Import via `codomyrmex.agents.hermes._provider_router` (shim).

## Development Guidelines

- Keep each file scoped to its single responsibility; route new provider logic through `router.py`'s `call_llm()` dispatch rather than growing a new god-module.
