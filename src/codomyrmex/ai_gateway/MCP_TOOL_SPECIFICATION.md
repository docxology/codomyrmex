# AI Gateway — MCP Tool Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `ai_gateway` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

The AI Gateway module provides load-balanced routing of completion requests across
multiple AI providers with failover and health checking capabilities.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `ai_gateway` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `gateway_complete`

**Description**: Route a completion request through the AI Gateway with load balancing and failover.
**Trust Level**: Safe
**Category**: generation

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | `str` | Yes | -- | The prompt text to complete |
| `providers` | `list[dict[str, Any]]` | No | `None` | List of provider configs, each with `name`, `endpoint`, and optionally `weight`. Returns error if omitted. |
| `strategy` | `str` | No | `"round_robin"` | Load balancing strategy: `"round_robin"` or `"weighted"` |

**Returns**: `dict` — Dictionary with `status`, provider used, response text, latency, and success flag.

**Example**:
```python
from codomyrmex.ai_gateway.mcp_tools import gateway_complete

result = gateway_complete(
    prompt="Explain recursion",
    providers=[
        {"name": "openai", "endpoint": "https://api.openai.com/v1/chat/completions", "weight": 2.0},
        {"name": "anthropic", "endpoint": "https://api.anthropic.com/v1/messages", "weight": 1.0}
    ],
    strategy="weighted"
)
```

**Notes**: Requires at least one provider configuration. Returns an error if `providers` is empty or `None`.

---

### `gateway_health`

**Description**: Check the health status of all configured AI Gateway providers.
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `providers` | `list[dict[str, Any]]` | No | `None` | List of provider configs, each with `name` and `endpoint`. Returns error if omitted. |

**Returns**: `dict` — Dictionary with `status` and `providers` (dict mapping provider names to their health and circuit breaker state).

**Example**:
```python
from codomyrmex.ai_gateway.mcp_tools import gateway_health

result = gateway_health(
    providers=[
        {"name": "openai", "endpoint": "https://api.openai.com/v1/chat/completions"},
        {"name": "anthropic", "endpoint": "https://api.anthropic.com/v1/messages"}
    ]
)
```

**Notes**: Requires at least one provider configuration. Returns an error if `providers` is empty or `None`.

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe — no trust check required
- **PAI Phases**: EXECUTE (route AI requests), OBSERVE (provider health monitoring)
- **Dependencies**: `ai_gateway.gateway.AIGateway`, `ai_gateway.gateway.GatewayConfig`, `ai_gateway.gateway.Provider`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
