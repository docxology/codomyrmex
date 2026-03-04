# Matrix Multiplication Kernel Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides a tiled (cache-efficient) matrix multiplication kernel in pure Python/NumPy. Implements BLAS-style blocked matmul for improved cache locality, plus batched multiplication and FLOP counting.

## Functional Requirements

1. Tiled matrix multiplication with configurable block size for cache efficiency
2. Batched matrix multiplication support for 3D tensor inputs
3. FLOP counting via matmul_flops(M, K, N) = 2*M*K*N


## Interface

```python
from codomyrmex.matmul_kernel import tiled_matmul, batched_matmul, matmul_flops

C = tiled_matmul(A, B, tile_size=32)
flops = matmul_flops(M=128, K=64, N=256)
```

## Exports

tiled_matmul, batched_matmul, matmul_flops

## Navigation

- [Source README](../../src/codomyrmex/matmul_kernel/README.md) | [AGENTS.md](AGENTS.md)
