"""FP4 (4-bit float) quantization.

Implements FP4 quantization with 16 representable values using
1 sign bit, 1 exponent bit, and 2 mantissa bits. Values are
nibble-packed (2 per byte) for memory efficiency.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

# FP4 format: 1 sign bit, 1 exponent bit, 2 mantissa bits
# 16 representable values indexed 0-15:
#   Index 0-7:  positive values {0, 0.0625, 0.125, 0.25, 0.5, 1.0, 1.5, 2.0}
#   Index 8-15: negative mirrors {-0, -0.0625, -0.125, -0.25, -0.5, -1.0, -1.5, -2.0}
FP4_VALUES = np.array(
    [
        0.0,
        0.0625,
        0.125,
        0.25,
        0.5,
        1.0,
        1.5,
        2.0,
        -0.0,
        -0.0625,
        -0.125,
        -0.25,
        -0.5,
        -1.0,
        -1.5,
        -2.0,
    ],
    dtype=np.float32,
)


@dataclass
class FP4Tensor:
    """FP4-quantized tensor stored as uint8 (2 fp4 values packed per byte).

    Attributes:
        packed: uint8 array where each byte holds 2 nibble-packed FP4 indices.
                Lower nibble = first value, upper nibble = second value.
        scale: Global scale factor mapping original range to [-2, 2].
        shape: Original tensor shape before flattening and packing.
        size: Total number of FP4 values (may differ from packed length * 2 for odd sizes).
    """

    packed: np.ndarray
    scale: float
    shape: tuple
    size: int


def _find_nearest_fp4_indices(x_scaled: np.ndarray) -> np.ndarray:
    """Find the nearest FP4 value index for each element.

    Args:
        x_scaled: Scaled float array in approximately [-2, 2] range.

    Returns:
        Array of uint8 indices into FP4_VALUES (0-15).
    """
    # Broadcast: |x_scaled - each fp4_value| -> shape (n, 16)
    x_flat = x_scaled.ravel()
    diffs = np.abs(x_flat[:, np.newaxis] - FP4_VALUES[np.newaxis, :])
    indices = np.argmin(diffs, axis=1).astype(np.uint8)
    return indices


def quantize_fp4(x: np.ndarray) -> FP4Tensor:
    """Quantize float32 tensor to FP4.

    Algorithm:
    1. Compute global scale = max(|x|) / 2.0 (maps to range [-2, 2])
    2. Scale input: x_scaled = x / scale
    3. For each value, find nearest FP4 value (nearest-neighbor quantization)
    4. Pack 2 fp4 indices per byte (lower nibble = 1st value, upper nibble = 2nd)

    Args:
        x: Input float32 numpy array of any shape.

    Returns:
        FP4Tensor with packed uint8 data.
    """
    original_shape = x.shape
    n = x.size
    x_flat = x.ravel().astype(np.float32)

    # Compute global scale
    abs_max = float(np.max(np.abs(x_flat)))
    scale = 1.0 if abs_max < 1e-10 else abs_max / 2.0

    # Scale to [-2, 2] range
    x_scaled = x_flat / scale

    # Find nearest FP4 indices
    indices = _find_nearest_fp4_indices(x_scaled)

    # Pack 2 indices per byte: lower nibble = even index, upper nibble = odd index
    n_packed = math.ceil(n / 2)
    packed = np.zeros(n_packed, dtype=np.uint8)

    for i in range(n_packed):
        low_idx = 2 * i
        high_idx = 2 * i + 1
        low_val = indices[low_idx]
        high_val = indices[high_idx] if high_idx < n else 0
        packed[i] = (high_val << 4) | (low_val & 0x0F)

    return FP4Tensor(
        packed=packed,
        scale=scale,
        shape=original_shape,
        size=n,
    )


def dequantize_fp4(ft: FP4Tensor) -> np.ndarray:
    """Reconstruct float32 approximation from FP4.

    Unpacks nibble-packed indices, looks up FP4 values, and scales back.

    Args:
        ft: FP4Tensor from quantize_fp4.

    Returns:
        float32 array of original shape.
    """
    n = ft.size
    values = np.zeros(n, dtype=np.float32)

    for i in range(len(ft.packed)):
        byte = ft.packed[i]
        low_idx = byte & 0x0F
        high_idx = (byte >> 4) & 0x0F

        pos_low = 2 * i
        pos_high = 2 * i + 1

        if pos_low < n:
            values[pos_low] = FP4_VALUES[low_idx]
        if pos_high < n:
            values[pos_high] = FP4_VALUES[high_idx]

    # Scale back to original range
    values *= ft.scale

    return values.reshape(ft.shape)


class FP4Quantizer:
    """Stateful FP4 quantizer.

    Provides a simple interface for FP4 quantization and dequantization
    with compression ratio reporting.
    """

    def quantize(self, x: np.ndarray) -> FP4Tensor:
        """Quantize float32 array to FP4.

        Args:
            x: Input float32 array.

        Returns:
            FP4Tensor with nibble-packed data.
        """
        return quantize_fp4(x)

    def dequantize(self, ft: FP4Tensor) -> np.ndarray:
        """Dequantize FP4Tensor back to float32.

        Args:
            ft: FP4Tensor to reconstruct.

        Returns:
            float32 array of original shape.
        """
        return dequantize_fp4(ft)

    def compression_ratio(self, x: np.ndarray) -> float:
        """Return compression ratio: float32 (32 bits) to fp4 (4 bits) = 8x.

        Args:
            x: Input array (used for interface consistency, value is constant).

        Returns:
            8.0 (always, since FP4 is 4 bits vs float32 at 32 bits).
        """
        return 8.0
