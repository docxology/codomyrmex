# LoRA -- MCP Tool Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `lora` (Low-Rank Adaptation) module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `lora` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `lora_apply`

**Description**: Apply LoRA to a weight matrix of given shape.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `weight_shape` | `list` | Yes | -- | [d, k] shape of the weight matrix |
| `rank` | `int` | No | `4` | LoRA rank r (must be < min(d, k)) |
| `alpha` | `float` | No | `8.0` | LoRA scaling alpha |

**Returns**: `dict` -- Dictionary with weight_shape, rank, scaling, lora_params, total_params, parameter_reduction_pct, and delta_shape.

**Example**:
```python
from codomyrmex.lora.mcp_tools import lora_apply

result = lora_apply(weight_shape=[768, 768], rank=8, alpha=16.0)
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe -- no destructive operations
- **PAI Phases**: BUILD (adapter application), OBSERVE (parameter efficiency analysis)
- **Dependencies**: Requires `numpy` and internal `lora` module (apply_lora)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
