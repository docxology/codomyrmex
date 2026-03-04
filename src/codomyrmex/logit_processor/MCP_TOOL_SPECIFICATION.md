# Logit Processor -- MCP Tool Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `logit_processor` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `logit_processor` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `process_logits`

**Description**: Apply sampling strategies to language model logits.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `logits` | `list[float]` | Yes | -- | Raw logit values from language model |
| `temperature` | `float` | No | `1.0` | Scaling factor (>1=diverse, <1=focused, 1=unchanged) |
| `top_k` | `int` | No | `0` | Keep only top-k tokens (0=disabled) |
| `top_p` | `float` | No | `1.0` | Nucleus sampling threshold (1.0=disabled) |
| `repetition_penalty` | `float` | No | `1.0` | Penalize repeated tokens (1.0=disabled, >1.0=penalize) |
| `previous_tokens` | `list[int] \| None` | No | `None` | Previously generated token IDs for repetition penalty |
| `seed` | `int \| None` | No | `None` | Random seed for reproducibility |

**Returns**: `dict` -- Dictionary with sampled_token, greedy_token, top5_tokens (list of {id, prob}), and entropy.

**Example**:
```python
from codomyrmex.logit_processor.mcp_tools import process_logits

result = process_logits(
    logits=[2.0, 1.0, 0.5, -1.0, 3.0],
    temperature=0.8,
    top_k=3,
    seed=42,
)
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe -- no destructive operations
- **PAI Phases**: BUILD (token sampling), VERIFY (sampling distribution analysis)
- **Dependencies**: Requires `numpy` and internal `processor` module

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
