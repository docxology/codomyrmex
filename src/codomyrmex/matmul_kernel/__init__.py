"""Tiled matrix multiplication kernel — cache-efficient BLAS-style matmul in pure Python/NumPy."""
from .kernel import tiled_matmul, batched_matmul, matmul_flops

__all__ = ["tiled_matmul", "batched_matmul", "matmul_flops"]
