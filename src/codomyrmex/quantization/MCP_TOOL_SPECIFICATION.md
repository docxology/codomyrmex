# Quantization -- MCP Tool Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `quantization` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `quantization` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `quantize_tensor`

**Description**: Quantize a list of float values to int8 or fp4.
**Trust Level**: Safe
**Category**: data-mutation

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `values` | `list[float]` | Yes | -- | List of float32 values to quantize |
| `method` | `str` | No | `"int8"` | Quantization method -- "int8" or "fp4" |
| `scheme` | `str` | No | `"asymmetric"` | For int8: "symmetric" or "asymmetric" (ignored for fp4) |

**Returns**: `dict` -- Dictionary with method, quantized values, scale, reconstruction error metrics, and status.

**Example**:
```python
from codomyrmex.quantization.mcp_tools import quantize_tensor

result = quantize_tensor(
    values=[1.5, -0.3, 2.1, 0.0, -1.7],
    method="int8",
    scheme="symmetric",
)
```

---

### `quantization_benchmark`

**Description**: Benchmark int8 vs fp4 quantization on random data.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `size` | `int` | No | `1000` | Number of float32 values to benchmark |

**Returns**: `dict` -- Comparison of int8 symmetric, int8 asymmetric, and fp4 error metrics with timing.

**Example**:
```python
from codomyrmex.quantization.mcp_tools import quantization_benchmark

result = quantization_benchmark(size=5000)
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe -- no destructive operations
- **PAI Phases**: BUILD (model quantization), VERIFY (error analysis benchmarking)
- **Dependencies**: Requires `numpy` and internal `int8`, `fp4`, `utils` modules

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
