"""Codomyrmex MLX Quantizer.

This module provides wrappers for creating INT8 and INT4 quantized
MLX arrays and models, focused on running edge ML workloads
within constrained memory boundaries (<2GB).
"""

import dataclasses
from typing import Any

try:
    import mlx.core as mx
except ImportError:
    mx: Any = None


@dataclasses.dataclass
class QuantizationConfig:
    """Configuration for MLX array quantization."""

    bits: int = 4
    group_size: int = 64

    def __post_init__(self):
        if self.bits not in (4, 8, 16):
            raise ValueError("QuantizationConfig bits must be exactly 4, 8, or 16.")
        if self.group_size <= 0:
            raise ValueError("QuantizationConfig group_size must be positive.")


def quantize_array(array, config: QuantizationConfig):
    if mx is None:
        raise ImportError("mlx is not installed")
    if config.bits == 16:
        return array.astype(mx.float16), None, None
    return mx.quantize(array, group_size=config.group_size, bits=config.bits)


def dequantize_array(wq, scales, biases, config: QuantizationConfig):
    if mx is None:
        raise ImportError("mlx is not installed")
    if config.bits == 16:
        return wq
    if scales is None or biases is None:
        raise ValueError("Scales and biases must be provided for bits < 16")
    return mx.dequantize(
        wq, scales, biases, group_size=config.group_size, bits=config.bits
    )
