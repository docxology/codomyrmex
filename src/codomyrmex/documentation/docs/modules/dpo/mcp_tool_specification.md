# DPO -- MCP Tool Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `dpo` (Direct Preference Optimization) module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `dpo` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `dpo_compute_loss`

**Description**: Compute DPO loss on synthetic preference data.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `beta` | `float` | No | `0.1` | KL penalty coefficient (typical range 0.01-0.5) |
| `batch_size` | `int` | No | `4` | Number of preference pairs |
| `seed` | `int` | No | `42` | Random seed for reproducibility |

**Returns**: `dict` -- Dictionary with loss, accuracy, rewards_w mean, rewards_l mean, and status.

**Example**:
```python
from codomyrmex.dpo.mcp_tools import dpo_compute_loss

result = dpo_compute_loss(beta=0.2, batch_size=8, seed=123)
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe -- no destructive operations
- **PAI Phases**: BUILD (preference optimization), VERIFY (loss validation)
- **Dependencies**: Requires `numpy` and internal `loss` module

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
