"""MCP tool wrappers for quantization operations.

Exposes quantize_tensor and quantization_benchmark as auto-discovered
MCP tools via the @mcp_tool decorator.
"""

from __future__ import annotations

import time

import numpy as np

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .fp4 import dequantize_fp4, quantize_fp4
from .int8 import dequantize_int8, quantize_int8
from .utils import quantization_error


@mcp_tool(category="quantization")
def quantize_tensor(
    values: list[float],
    method: str = "int8",
    scheme: str = "asymmetric",
) -> dict:
    """Quantize a list of float values to int8 or fp4.

    Args:
        values: list of float32 values to quantize.
        method: Quantization method -- "int8" or "fp4".
        scheme: For int8: "symmetric" or "asymmetric" (ignored for fp4).

    Returns:
        Dictionary with method, quantized values, scale, reconstruction
        error metrics, and status.
    """
    x = np.array(values, dtype=np.float32)

    if method == "int8":
        qt = quantize_int8(x, scheme=scheme)
        reconstructed = dequantize_int8(qt)
        error = quantization_error(x, reconstructed)
        return {
            "status": "success",
            "method": "int8",
            "scheme": scheme,
            "quantized_values": qt.data.tolist(),
            "scale": float(qt.scale)
            if not isinstance(qt.scale, np.ndarray)
            else qt.scale.tolist(),
            "zero_point": int(qt.zero_point)
            if not isinstance(qt.zero_point, np.ndarray)
            else qt.zero_point.tolist(),
            "reconstructed": reconstructed.tolist(),
            "error": error,
        }

    if method == "fp4":
        ft = quantize_fp4(x)
        reconstructed = dequantize_fp4(ft)
        error = quantization_error(x, reconstructed)
        return {
            "status": "success",
            "method": "fp4",
            "scale": ft.scale,
            "num_fp4_values": ft.size,
            "compression_ratio": "8x vs float32",
            "reconstructed": reconstructed.tolist(),
            "error": error,
        }

    return {
        "status": "error",
        "message": f"Unknown method: {method}. Use 'int8' or 'fp4'",
    }


@mcp_tool(category="quantization")
def quantization_benchmark(size: int = 1000) -> dict:
    """Benchmark int8 vs fp4 quantization on random data.

    Generates random float32 data and measures quantization error
    for both int8 (symmetric + asymmetric) and fp4 methods.

    Args:
        size: Number of float32 values to benchmark.

    Returns:
        Comparison of int8 symmetric, int8 asymmetric, and fp4 error metrics.
    """
    rng = np.random.default_rng(42)
    x = rng.standard_normal(size).astype(np.float32)

    # Int8 asymmetric
    t0 = time.perf_counter()
    qt_asym = quantize_int8(x, scheme="asymmetric")
    recon_asym = dequantize_int8(qt_asym)
    t_int8_asym = time.perf_counter() - t0
    err_asym = quantization_error(x, recon_asym)

    # Int8 symmetric
    t0 = time.perf_counter()
    qt_sym = quantize_int8(x, scheme="symmetric")
    recon_sym = dequantize_int8(qt_sym)
    t_int8_sym = time.perf_counter() - t0
    err_sym = quantization_error(x, recon_sym)

    # FP4
    t0 = time.perf_counter()
    ft = quantize_fp4(x)
    recon_fp4 = dequantize_fp4(ft)
    t_fp4 = time.perf_counter() - t0
    err_fp4 = quantization_error(x, recon_fp4)

    return {
        "status": "success",
        "size": size,
        "int8": {
            "asymmetric": {
                "error": err_asym,
                "time_seconds": t_int8_asym,
            },
            "symmetric": {
                "error": err_sym,
                "time_seconds": t_int8_sym,
            },
        },
        "fp4": {
            "error": err_fp4,
            "time_seconds": t_fp4,
            "compression_ratio": "8x",
        },
    }
