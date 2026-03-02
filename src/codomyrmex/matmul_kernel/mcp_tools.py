import numpy as np
from codomyrmex.model_context_protocol.decorators import mcp_tool
from .kernel import tiled_matmul, batched_matmul, benchmark_matmul, matmul_flops


@mcp_tool(category="matmul_kernel")
def matmul_compute(a: list[list[float]], b: list[list[float]], tile_size: int = 32) -> dict:
    """Multiply two matrices using tiled algorithm.

    Args:
        a: 2D list representing matrix A (MxK)
        b: 2D list representing matrix B (KxN)
        tile_size: Cache tile size

    Returns:
        dict with: result (2D list), shape, flops, correct (vs numpy)
    """
    A = np.array(a, dtype=np.float32)
    B = np.array(b, dtype=np.float32)
    C = tiled_matmul(A, B, tile_size=tile_size)
    C_ref = A @ B
    max_err = float(np.max(np.abs(C - C_ref)))
    return {
        "status": "success",
        "result": C.tolist(),
        "shape": list(C.shape),
        "flops": matmul_flops(A.shape[0], A.shape[1], B.shape[1]),
        "max_error_vs_numpy": max_err,
        "correct": max_err < 1e-4,
    }


@mcp_tool(category="matmul_kernel")
def matmul_benchmark(max_size: int = 128) -> dict:
    """Benchmark tiled matmul against numpy for square matrices.

    Args:
        max_size: Largest matrix size to test (max 512 to keep fast)

    Returns:
        Performance comparison results per matrix size
    """
    max_size = min(max_size, 512)
    sizes = [s for s in [16, 32, 64, 128, 256, 512] if s <= max_size]
    return {"status": "success", "results": benchmark_matmul(sizes)}
