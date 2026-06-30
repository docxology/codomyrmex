# Matmul Kernel -- MCP Tool Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `matmul_kernel` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `matmul_kernel` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `matmul_compute`

**Description**: Multiply two matrices using tiled algorithm.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `a` | `list[list[float]]` | Yes | -- | 2D list representing matrix A (MxK) |
| `b` | `list[list[float]]` | Yes | -- | 2D list representing matrix B (KxN) |
| `tile_size` | `int` | No | `32` | Cache tile size |

**Returns**: `dict` -- Dictionary with result (2D list), shape, flops, max_error_vs_numpy, and correct (bool).

**Example**:
```python
from codomyrmex.matmul_kernel.mcp_tools import matmul_compute

result = matmul_compute(
    a=[[1.0, 2.0], [3.0, 4.0]],
    b=[[5.0, 6.0], [7.0, 8.0]],
    tile_size=16,
)
```

---

### `matmul_benchmark`

**Description**: Benchmark tiled matmul against numpy for square matrices.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `max_size` | `int` | No | `128` | Largest matrix size to test (max 512 to keep fast) |

**Returns**: `dict` -- Performance comparison results per matrix size with status.

**Example**:
```python
from codomyrmex.matmul_kernel.mcp_tools import matmul_benchmark

result = matmul_benchmark(max_size=256)
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe -- no destructive operations
- **PAI Phases**: VERIFY (performance benchmarking), BUILD (matrix computation)
- **Dependencies**: Requires `numpy` and internal `kernel` module (tiled_matmul, benchmark_matmul, matmul_flops)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
