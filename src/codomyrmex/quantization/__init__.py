"""Quantization library -- Int8 and FP4 quantization for neural network weights.

Provides symmetric/asymmetric Int8 quantization and FP4 (4-bit float)
quantization with nibble-packed storage, plus error metrics utilities.
"""

from .fp4 import FP4Quantizer, FP4Tensor, dequantize_fp4, quantize_fp4
from .int8 import Int8Quantizer, QuantizedTensor, dequantize_int8, quantize_int8
from .utils import compute_scale_zero_point, per_channel_scale, quantization_error

__all__ = [
    "Int8Quantizer",
    "QuantizedTensor",
    "quantize_int8",
    "dequantize_int8",
    "FP4Quantizer",
    "FP4Tensor",
    "quantize_fp4",
    "dequantize_fp4",
    "compute_scale_zero_point",
    "per_channel_scale",
    "quantization_error",
]
