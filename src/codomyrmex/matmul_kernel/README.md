# Matmul Kernel Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Matmul Kernel module provides a tiled matrix multiplication implementation in pure Python/NumPy. It demonstrates the cache-blocking algorithm used in high-performance BLAS libraries and GPU kernels (e.g., CUDA shared memory tiling).

The tiling approach splits large matrices into smaller tiles that fit in L1/L2 cache, improving data locality and reducing cache misses. While NumPy's built-in `@` operator uses optimized BLAS under the hood, this module makes the tiling algorithm explicit for educational and benchmarking purposes.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **BUILD** | Compute matrix products for numerical pipelines | `matmul_compute` |
| **VERIFY** | Benchmark tiled vs BLAS performance | `matmul_benchmark` |

## Features

- **Tiled matrix multiplication**: Cache-blocking with configurable tile size
- **Batched matmul**: 3D tensor batch support (C[b] = A[b] @ B[b])
- **FLOP counting**: Compute theoretical floating-point operations
- **Benchmarking**: Compare tiled implementation against NumPy BLAS reference
- **Correctness validation**: Max error checking against NumPy reference

## API

### `tiled_matmul(A, B, tile_size=64, out=None)`

Tiled matrix multiplication C = A @ B using cache-blocking.

- **A**: (M, K) float32 matrix
- **B**: (K, N) float32 matrix
- **tile_size**: Cache tile size (default 64)
- **out**: Optional pre-allocated output array
- **Returns**: (M, N) result matrix

### `batched_matmul(A, B)`

Batched matrix multiplication for 3D tensors.

- **A**: (batch, M, K) tensor
- **B**: (batch, K, N) tensor
- **Returns**: (batch, M, N) tensor

### `matmul_flops(M, K, N)`

Compute theoretical FLOPs for an MxK @ KxN multiplication (2*M*K*N).

## MCP Tools

| Tool | Description |
|------|-------------|
| `matmul_compute` | Multiply two matrices using tiled algorithm |
| `matmul_benchmark` | Benchmark tiled matmul against numpy for square matrices |

## Dependencies

- `numpy` (core dependency)
