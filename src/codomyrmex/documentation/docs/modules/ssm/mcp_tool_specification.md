# SSM (State Space Models) — MCP Tool Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `ssm` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `ssm` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `ssm_forward`

**Description**: Run a forward pass through Mamba State Space Model.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `sequence_length` | `int` | No | `8` | Sequence length to process |
| `d_model` | `int` | No | `16` | Model dimension |
| `d_state` | `int` | No | `8` | SSM state dimension |
| `n_layers` | `int` | No | `2` | Number of Mamba blocks to stack |

**Returns**: `dict` — Dictionary with `output_shape`, `d_model`, `d_state`, `n_layers`, and `status`.

**Example**:
```python
from codomyrmex.ssm.mcp_tools import ssm_forward

result = ssm_forward(sequence_length=16, d_model=32, d_state=16, n_layers=4)
```

**Notes**: Requires numpy. Generates random input data internally for the forward pass.

---

### `flash_attention_forward`

**Description**: Run Flash Attention and verify against standard attention.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `seq_len` | `int` | No | `16` | Sequence length |
| `d_model` | `int` | No | `32` | Q/K/V dimension |
| `block_size` | `int` | No | `8` | Flash attention tile size |

**Returns**: `dict` — Dictionary with `output_shape`, `max_error_vs_standard` (should be < 1e-5), `passed` (bool), and `status`.

**Example**:
```python
from codomyrmex.ssm.mcp_tools import flash_attention_forward

result = flash_attention_forward(seq_len=32, d_model=64, block_size=16)
```

**Notes**: Imports from `codomyrmex.neural.flash_attention`. Generates random Q/K/V matrices internally. The `passed` field indicates whether the flash attention output matches standard attention within tolerance.

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe — no trust check required
- **PAI Phases**: VERIFY (model correctness validation), BUILD (neural architecture experimentation)
- **Dependencies**: `numpy`, `codomyrmex.neural.flash_attention` (for flash_attention_forward)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
