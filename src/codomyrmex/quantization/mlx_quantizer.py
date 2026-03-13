"""Codomyrmex MLX Quantizer.

This module provides wrappers for creating INT8 and INT4 quantized
MLX arrays and models, focused on running edge ML workloads
within constrained memory boundaries (<2GB).
"""

import dataclasses

import mlx.core as mx


@dataclasses.dataclass
class QuantizationConfig:
    """Configuration for MLX array quantization.

    Attributes:
        bits: Number of bits per parameter (4 or 8).
              If 16, falls back to raw fp16 without quantization.
        group_size: Group size for quantization parameters (default 64).
    """

    bits: int = 4
    group_size: int = 64

    def __post_init__(self):
        if self.bits not in (4, 8, 16):
            raise ValueError("QuantizationConfig bits must be exactly 4, 8, or 16.")
        if self.group_size <= 0:
            raise ValueError("QuantizationConfig group_size must be positive.")


def quantize_array(
    array: mx.array, config: QuantizationConfig
) -> tuple[mx.array, mx.array | None, mx.array | None]:
    """Quantize an MLX array into lower precision (e.g. INT4 or INT8).

    Args:
        array: The source continuous MLX array (e.g., float32 or float16).
        config: The quantization parameters (bits and group_size).

    Returns:
        A tuple of (quantized_weights, scales, biases).
        If config.bits is 16, falls back to direct float16 cast,
        returning (fp16_weights, None, None).
    """
    if config.bits == 16:
        # Fallback to standard FP16 without structural quantization
        return array.astype(mx.float16), None, None

    # Native MLX quantization for lower bit depths
    return mx.quantize(array, group_size=config.group_size, bits=config.bits)


def dequantize_array(
    wq: mx.array,
    scales: mx.array | None,
    biases: mx.array | None,
    config: QuantizationConfig,
) -> mx.array:
    """Dequantize an MLX array back into a continuous floating point format.

    Args:
        wq: The quantized weights array.
        scales: The associated scaling factors (None if bits=16 fallback).
        biases: The associated bias offsets (None if bits=16 fallback).
        config: The quantization parameters the weights were compressed with.

    Returns:
        The reconstructed MLX array in standard precision.
    """
    if config.bits == 16:
        # Array is already in raw form (fp16 fallback)
        return wq

    if scales is None or biases is None:
        raise ValueError("Scales and biases must be provided for bits < 16")

    # Native MLX dequantization
    return mx.dequantize(
        wq, scales, biases, group_size=config.group_size, bits=config.bits
    )
