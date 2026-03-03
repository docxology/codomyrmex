"""Tiled matrix multiplication kernel — cache-efficient BLAS-style matmul in pure Python/NumPy."""

from .kernel import batched_matmul, matmul_flops, tiled_matmul

__all__ = ["tiled_matmul", "batched_matmul", "matmul_flops"]
