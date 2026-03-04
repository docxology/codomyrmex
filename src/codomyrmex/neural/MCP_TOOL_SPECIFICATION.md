# Neural -- MCP Tool Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `neural` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `neural` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `transformer_encode`

**Description**: Run a forward pass through a randomly-initialized Transformer encoder.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `sequence_length` | `int` | No | `8` | Number of tokens in the sequence |
| `d_model` | `int` | No | `64` | Model dimension (must be divisible by n_heads) |
| `n_heads` | `int` | No | `4` | Number of attention heads |
| `n_layers` | `int` | No | `2` | Number of transformer blocks |

**Returns**: `dict` -- Dictionary with output_shape, d_model, n_heads, n_layers, sequence_length, and status.

**Example**:
```python
from codomyrmex.neural.mcp_tools import transformer_encode

result = transformer_encode(sequence_length=16, d_model=128, n_heads=8, n_layers=4)
```

---

### `attention_forward`

**Description**: Run multi-head attention on random inputs.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `seq_len` | `int` | No | `6` | Sequence length |
| `d_model` | `int` | No | `32` | Model dimension |
| `n_heads` | `int` | No | `4` | Number of attention heads |

**Returns**: `dict` -- Dictionary with output_shape, attention_weights_shape, d_k (head dimension), and status.

**Example**:
```python
from codomyrmex.neural.mcp_tools import attention_forward

result = attention_forward(seq_len=10, d_model=64, n_heads=8)
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe -- no destructive operations
- **PAI Phases**: BUILD (neural network operations), VERIFY (architecture validation)
- **Dependencies**: Requires `numpy` and internal `transformer` module (TransformerEncoder) and `attention` module (MultiHeadAttention)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
