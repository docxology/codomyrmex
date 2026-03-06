# Distributed Training -- MCP Tool Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `distributed_training` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `distributed_training` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `fsdp_simulate_step`

**Description**: Simulate one FSDP distributed training step.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `param_size` | `int` | No | `1024` | Number of model parameters |
| `world_size` | `int` | No | `4` | Number of simulated GPU devices |
| `learning_rate` | `float` | No | `0.01` | SGD learning rate |
| `seed` | `int` | No | `42` | Random seed for reproducibility |

**Returns**: `dict` -- Dictionary with shard_sizes, param_norm_before, param_norm_after, grad_norm, and status.

**Example**:
```python
from codomyrmex.distributed_training.mcp_tools import fsdp_simulate_step

result = fsdp_simulate_step(param_size=2048, world_size=8, learning_rate=0.001)
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe -- no destructive operations
- **PAI Phases**: BUILD (training simulation), VERIFY (performance validation)
- **Dependencies**: Requires `numpy` and internal `fsdp` module

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
