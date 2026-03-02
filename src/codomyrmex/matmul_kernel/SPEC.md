# Matmul Kernel Module -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Algorithm

### Tiled Matrix Multiplication

Given matrices A (M x K) and B (K x N), compute C = A @ B using cache-blocking:

```
for i in range(0, M, tile_size):
    for k in range(0, K, tile_size):
        for j in range(0, N, tile_size):
            C[i:i+ts, j:j+ts] += A[i:i+ts, k:k+ts] @ B[k:k+ts, j:j+ts]
```

The i-k-j loop order ensures that tiles of A are reused across the inner j-loop, maximizing temporal locality.

### Complexity

| Metric | Value |
|--------|-------|
| Time complexity | O(M * K * N) |
| Space complexity | O(M * N) for output |
| FLOPs | 2 * M * K * N (1 multiply + 1 add per output element contribution) |

### Numerical Properties

| Property | Value |
|----------|-------|
| Input dtype | float32 (default), float64 supported |
| Output dtype | Matches input (float32 -> float32, float64 -> float64) |
| Max error vs numpy | < 1e-4 for float32, < 1e-10 for float64 |
| Tile size range | 1 to min(M, K, N); default 64 |

### Tile Size Selection

- **Small matrices (< 64)**: tile_size = matrix dimension (single tile)
- **L1 cache fit**: tile_size = 32 (3 tiles of 32x32 float32 = 12KB, fits in 32KB L1)
- **L2 cache fit**: tile_size = 64 (3 tiles of 64x64 float32 = 48KB, fits in 256KB L2)
- **Large matrices**: tile_size = 64-128 depending on cache hierarchy

### Batched Operation

Batched matmul processes each batch element independently:
- Input: A (batch, M, K), B (batch, K, N)
- Output: C (batch, M, N) where C[b] = A[b] @ B[b]
- No cross-batch dependencies; trivially parallelizable

## MCP Tool Specifications

### matmul_compute

```json
{
  "name": "matmul_compute",
  "category": "matmul_kernel",
  "parameters": {
    "a": {"type": "list[list[float]]", "description": "Matrix A (MxK)"},
    "b": {"type": "list[list[float]]", "description": "Matrix B (KxN)"},
    "tile_size": {"type": "int", "default": 32, "description": "Cache tile size"}
  },
  "returns": {
    "status": "success",
    "result": "2D list (MxN)",
    "shape": "[M, N]",
    "flops": "int",
    "max_error_vs_numpy": "float",
    "correct": "bool"
  }
}
```

### matmul_benchmark

```json
{
  "name": "matmul_benchmark",
  "category": "matmul_kernel",
  "parameters": {
    "max_size": {"type": "int", "default": 128, "max": 512}
  },
  "returns": {
    "status": "success",
    "results": {"<size>": {"size": "int", "flops": "int", "tiled_ms": "float", "numpy_ms": "float", "max_error": "float", "correct": "bool"}}
  }
}
```
