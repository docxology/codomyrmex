import time

import numpy as np


def tiled_matmul(
    A: np.ndarray,
    B: np.ndarray,
    tile_size: int = 64,
    out: np.ndarray | None = None
) -> np.ndarray:
    """
    Tiled matrix multiplication C = A @ B using cache-blocking.

    Splits matrices into tiles of tile_size x tile_size to improve
    cache locality. Each tile fits in L1/L2 cache.

    Algorithm:
        for i in range(0, M, tile_size):
            for k in range(0, K, tile_size):
                for j in range(0, N, tile_size):
                    C[i:i+ts, j:j+ts] += A[i:i+ts, k:k+ts] @ B[k:k+ts, j:j+ts]

    Args:
        A: (M, K) float32 matrix
        B: (K, N) float32 matrix
        tile_size: Cache tile size (default 64)
        out: Optional pre-allocated output (M, N) array

    Returns:
        C: (M, N) result matrix

    Note: For benchmarking purposes. numpy.dot uses BLAS which is faster,
          but this demonstrates the tiling algorithm used in GPU kernels.
          # CUDA_ACCELERATE: GPU version tiles into shared memory blocks
    """
    assert A.ndim == 2 and B.ndim == 2, "Inputs must be 2D matrices"
    assert A.shape[1] == B.shape[0], f"Shape mismatch: {A.shape} @ {B.shape}"

    M, K = A.shape
    K2, N = B.shape

    if out is None:
        C = np.zeros((M, N), dtype=np.float64 if A.dtype == np.float64 else np.float32)
    else:
        C = out
        C[:] = 0

    # Tile loop
    for i in range(0, M, tile_size):
        for k in range(0, K, tile_size):
            for j in range(0, N, tile_size):
                # Compute tile bounds
                i_end = min(i + tile_size, M)
                k_end = min(k + tile_size, K)
                j_end = min(j + tile_size, N)

                # Tile multiply-accumulate
                C[i:i_end, j:j_end] += A[i:i_end, k:k_end] @ B[k:k_end, j:j_end]

    return C


def batched_matmul(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Batched matrix multiplication for 3D tensors.
    C[b] = A[b] @ B[b]

    Args:
        A: (batch, M, K)
        B: (batch, K, N)

    Returns:
        C: (batch, M, N)
    """
    assert A.ndim == 3 and B.ndim == 3
    assert A.shape[0] == B.shape[0], "Batch sizes must match"
    batch, M, K = A.shape
    _, K2, N = B.shape
    assert K == K2

    C = np.zeros((batch, M, N), dtype=A.dtype)
    for b in range(batch):
        C[b] = tiled_matmul(A[b], B[b])
    return C


def matmul_flops(M: int, K: int, N: int) -> int:
    """Compute number of floating point ops for MxK @ KxN matmul."""
    return 2 * M * K * N  # multiply + accumulate per element


def benchmark_matmul(sizes: list[int] = None) -> dict:
    """Benchmark tiled matmul vs numpy.dot for various sizes."""
    if sizes is None:
        sizes = [32, 64, 128, 256]

    results = {}
    for n in sizes:
        A = np.random.randn(n, n).astype(np.float32)
        B = np.random.randn(n, n).astype(np.float32)

        # Tiled
        t0 = time.perf_counter()
        C_tiled = tiled_matmul(A, B)
        t_tiled = time.perf_counter() - t0

        # NumPy reference
        t0 = time.perf_counter()
        C_ref = A @ B
        t_numpy = time.perf_counter() - t0

        # Error
        max_err = float(np.max(np.abs(C_tiled - C_ref)))
        flops = matmul_flops(n, n, n)

        results[n] = {
            "size": n,
            "flops": flops,
            "tiled_ms": round(t_tiled * 1000, 3),
            "numpy_ms": round(t_numpy * 1000, 3),
            "max_error": max_err,
            "correct": max_err < 1e-4,
        }

    return results
