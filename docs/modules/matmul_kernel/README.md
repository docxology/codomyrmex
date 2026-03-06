# MatMul Kernel Module

**Version**: v1.1.6 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `matmul_kernel` module provides a cache-efficient tiled matrix multiplication implementation in pure Python and NumPy. The tiling algorithm splits matrices into blocks that fit in L1/L2 cache, demonstrating the same cache-blocking strategy used in GPU CUDA kernels and BLAS libraries. Includes batched matmul for 3D tensors and a FLOP counting utility. This is primarily an educational and benchmarking module -- NumPy's built-in `@` operator uses optimized BLAS which is faster for production use.

## Architecture

The module is contained in `kernel.py` with four functions:

- **`tiled_matmul()`** -- the core tiled matrix multiplication with configurable tile size
- **`batched_matmul()`** -- applies tiled_matmul across the batch dimension of 3D tensors
- **`matmul_flops()`** -- computes the theoretical FLOP count (2*M*K*N)
- **`benchmark_matmul()`** -- compares tiled vs numpy.dot for various matrix sizes

The tiling loop order is i-k-j (row-inner-column), which maximizes temporal locality for the accumulation into C.

## Key Exports

| Export | Module | Description |
|--------|--------|-------------|
| `tiled_matmul` | `kernel.py` | Cache-blocked matrix multiplication C = A @ B |
| `batched_matmul` | `kernel.py` | Batched tiled matmul for 3D tensors |
| `matmul_flops` | `kernel.py` | FLOP count for M x K @ K x N multiplication |

## Quick Start

```python
import numpy as np
from codomyrmex.matmul_kernel import tiled_matmul, batched_matmul, matmul_flops

# Tiled matrix multiplication
A = np.random.randn(256, 128).astype(np.float32)
B = np.random.randn(128, 64).astype(np.float32)
C = tiled_matmul(A, B, tile_size=64)

# Verify correctness
ref = A @ B
print(f"Max error: {np.max(np.abs(C - ref)):.2e}")

# Batched version for 3D tensors
A_batch = np.random.randn(4, 32, 64).astype(np.float32)
B_batch = np.random.randn(4, 64, 16).astype(np.float32)
C_batch = batched_matmul(A_batch, B_batch)

# FLOP counting
flops = matmul_flops(256, 128, 64)
print(f"FLOPs: {flops:,}")  # 4,194,304
```

## Tiling Algorithm

The cache-blocking loop structure:

```
for i in range(0, M, tile_size):       # row tiles
    for k in range(0, K, tile_size):   # inner tiles
        for j in range(0, N, tile_size):   # column tiles
            C[i:i+ts, j:j+ts] += A[i:i+ts, k:k+ts] @ B[k:k+ts, j:j+ts]
```

Each tile multiply-accumulate operates on blocks that fit in CPU cache, reducing cache misses compared to naive element-wise iteration.

## MCP Tools

This module exposes MCP tools via `mcp_tools.py` and is auto-discovered by the PAI MCP bridge.

## PAI Integration

| Phase | Usage |
|-------|-------|
| VERIFY | Benchmark matrix operations and validate numerical correctness |
| BUILD | Educational reference for GPU kernel design patterns |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/matmul_kernel/ -v
```

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public exports: tiled_matmul, batched_matmul, matmul_flops |
| `kernel.py` | Tiled matmul, batched matmul, FLOP counter, and benchmark |
| `mcp_tools.py` | MCP tool definitions for PAI bridge |

## Related Modules

- [neural](../neural/) -- Transformer layers that depend on matrix multiplication
- [softmax_opt](../softmax_opt/) -- Optimized softmax (companion kernel optimization)
- [performance](../../modules/performance/) -- Benchmarking framework for kernel comparisons

## Navigation

- **AGENTS**: [AGENTS.md](AGENTS.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Source**: [`src/codomyrmex/matmul_kernel/`](../../../src/codomyrmex/matmul_kernel/)
- **Parent**: [Module Documentation](../README.md)
- **Root**: [docs/](../../README.md)
