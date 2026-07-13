"""Model Distillation and Quantization tools.

Provides memory-efficient array representations (INT4/INT8) utilizing Apple MLX
for edge inference execution constraints.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

from .fp4 import FP4Quantizer, FP4Tensor, dequantize_fp4, quantize_fp4
from .int8 import Int8Quantizer, QuantizedTensor, dequantize_int8, quantize_int8
from .utils import compute_scale_zero_point, per_channel_scale, quantization_error

_MLX_EXPORTS = frozenset(
    {"QuantizationConfig", "dequantize_array", "quantize_array"}
)


def __getattr__(name: str) -> Any:
    """Load the optional MLX backend only when an MLX symbol is requested."""
    if name in _MLX_EXPORTS:
        module = import_module(f"{__name__}.mlx_quantizer")
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "FP4Quantizer",
    "FP4Tensor",
    "Int8Quantizer",
    "QuantizationConfig",
    "QuantizedTensor",
    "compute_scale_zero_point",
    "dequantize_array",
    "dequantize_fp4",
    "dequantize_int8",
    "per_channel_scale",
    "quantization_error",
    "quantize_array",
    "quantize_fp4",
    "quantize_int8",
]
