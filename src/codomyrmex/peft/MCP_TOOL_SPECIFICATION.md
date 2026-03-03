# PEFT -- MCP Tool Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `peft` (Parameter-Efficient Fine-Tuning) module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `peft` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `peft_create_adapter`

**Description**: Create a PEFT adapter and return its parameter statistics.
**Trust Level**: Safe
**Category**: generation

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `method` | `str` | Yes | -- | One of "lora", "prefix", "ia3" |
| `d_model` | `int` | Yes | -- | Model hidden dimension |
| `rank` | `int` | No | `4` | LoRA rank (only used for lora method) |
| `alpha` | `float` | No | `8.0` | LoRA alpha scaling (only used for lora method) |

**Returns**: `dict` -- Dictionary with method, trainable_params, full_finetune_params, and reduction_factor.

**Example**:
```python
from codomyrmex.peft.mcp_tools import peft_create_adapter

result = peft_create_adapter(method="lora", d_model=768, rank=8, alpha=16.0)
```

---

### `peft_compare_methods`

**Description**: Compare all PEFT methods for a given model dimension.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `d_model` | `int` | Yes | -- | Model hidden dimension |
| `rank` | `int` | No | `4` | LoRA rank for comparison |

**Returns**: `dict` -- Dictionary mapping method name (full_finetune, lora, prefix, ia3) to trainable_params count.

**Example**:
```python
from codomyrmex.peft.mcp_tools import peft_compare_methods

result = peft_compare_methods(d_model=1024, rank=16)
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe -- no destructive operations
- **PAI Phases**: OBSERVE (adapter comparison), BUILD (adapter creation)
- **Dependencies**: Internal `adapters` module (LoRAAdapter, PrefixTuningAdapter, IA3Adapter)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
