# Matmul Kernel - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `matmul_kernel` module provides a cache-efficient BLAS-style matrix multiplication implementation in pure Python/NumPy. Includes tiled matmul for better cache utilisation and batched operations.

## 2. Core Components

### 2.1 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `tiled_matmul` | `(a, b, tile_size=64) -> ndarray` | Cache-efficient tiled matrix multiplication |
| `batched_matmul` | `(a_batch, b_batch) -> ndarray` | Batched matrix multiplication over leading dimensions |
| `matmul_flops` | `(m, n, k) -> int` | Compute FLOPs for an (m×k) × (k×n) multiplication |

## 3. Usage Example

```python
from codomyrmex.matmul_kernel import tiled_matmul, matmul_flops
import numpy as np

a = np.random.randn(256, 128)
b = np.random.randn(128, 64)

result = tiled_matmul(a, b, tile_size=32)
flops = matmul_flops(256, 64, 128)
print(f"Result shape: {result.shape}, FLOPs: {flops:,}")
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
