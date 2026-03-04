# Semantic Router -- MCP Tool Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `semantic_router` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `semantic_router` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `semantic_router_route`

**Description**: Route an input text to the best matching semantic route.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | `str` | No | `"What is the weather today?"` | Input text to classify |
| `routes` | `list[dict]` | No | `None` | List of route dicts, each with 'name' and 'utterances' keys. Default provides weather/greeting/help routes. |
| `embedding_dim` | `int` | No | `64` | Dimension of the embedding vectors |

**Returns**: `dict` -- Dictionary with route_name, score, matched (bool), all_routes (list), and status.

**Example**:
```python
from codomyrmex.semantic_router.mcp_tools import semantic_router_route

result = semantic_router_route(
    text="Hello, how are you?",
    routes=[
        {"name": "greeting", "utterances": ["Hello", "Hi there", "Hey"]},
        {"name": "farewell", "utterances": ["Goodbye", "See you later", "Bye"]},
    ],
)
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe -- no destructive operations
- **PAI Phases**: OBSERVE (intent classification), THINK (routing decisions)
- **Dependencies**: Internal `router` module (Route, SemanticRouter)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
