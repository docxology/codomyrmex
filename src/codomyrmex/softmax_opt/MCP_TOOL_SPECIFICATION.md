# Softmax Optimization — MCP Tool Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `softmax_opt` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

The softmax optimization module provides numerically stable softmax variants
including standard, log-softmax, and online softmax implementations.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `softmax_opt` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `compute_softmax`

**Description**: Compute softmax probabilities from logits with support for multiple variants.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `logits` | `list[float]` | Yes | -- | Raw unnormalized scores |
| `temperature` | `float` | No | `1.0` | Temperature scaling (>1 = more uniform, <1 = more peaked) |
| `variant` | `str` | No | `"standard"` | Softmax variant: `"standard"`, `"log"`, or `"online"` |

**Returns**: `dict` — Dictionary with `status`, `probabilities` (list), `log_probs` (list), `entropy` (float), `max_prob` (float), and `sum_check` (float, should be ~1.0).

**Example**:
```python
from codomyrmex.softmax_opt.mcp_tools import compute_softmax

result = compute_softmax(logits=[1.0, 2.0, 3.0], temperature=0.5, variant="standard")
```

**Notes**: Temperature scaling only applies to the `"standard"` variant. The `"online"` variant uses a numerically stable single-pass algorithm. The `"log"` variant computes log-softmax directly for better numerical precision.

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe — no trust check required
- **PAI Phases**: BUILD (neural network components), VERIFY (numerical stability checks)
- **Dependencies**: `numpy`, `softmax_opt.kernel` (softmax, log_softmax, online_softmax)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
