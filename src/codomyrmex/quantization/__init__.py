"""Model Distillation and Quantization tools.

Provides memory-efficient array representations (INT4/INT8) utilizing Apple MLX
for edge inference execution constraints.
"""

from .fp4 import FP4Quantizer, FP4Tensor, dequantize_fp4, quantize_fp4
from .int8 import Int8Quantizer, QuantizedTensor, dequantize_int8, quantize_int8
from .mlx_quantizer import QuantizationConfig, dequantize_array, quantize_array
from .utils import compute_scale_zero_point, per_channel_scale, quantization_error

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
