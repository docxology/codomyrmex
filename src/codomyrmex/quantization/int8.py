"""Int8 quantization — symmetric and asymmetric schemes.

Implements per-tensor and per-channel int8 quantization with
configurable symmetric (zero_point=0) and asymmetric schemes.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .utils import compute_scale_zero_point


@dataclass
class QuantizedTensor:
    """Container for a quantized tensor and its quantization parameters.

    Attributes:
        data: Quantized values stored as int8.
        scale: Scale factor (float32). Scalar for per-tensor, array for per-channel.
        zero_point: Zero point offset. 0 for symmetric scheme.
        scheme: "symmetric" or "asymmetric".
        original_dtype: Original floating-point dtype before quantization.
    """

    data: np.ndarray
    scale: float | np.ndarray
    zero_point: int | np.ndarray
    scheme: str
    original_dtype: np.dtype

    def dequantize(self) -> np.ndarray:
        """Reconstruct float32 approximation from quantized values."""
        return dequantize_int8(self)


def compute_scale_zero_point_int8(
    x: np.ndarray,
    scheme: str = "asymmetric",
    axis: int | None = None,
) -> tuple[float | np.ndarray, int | np.ndarray]:
    """Compute scale and zero_point for int8 quantization.

    Asymmetric: maps [x_min, x_max] to [-128, 127]
        scale = (x_max - x_min) / 255
        zero_point = clamp(round(-128 - x_min / scale), -128, 127)

    Symmetric: maps [-|x|_max, |x|_max] to [-127, 127]
        scale = |x|_max / 127
        zero_point = 0

    Args:
        x: Input float32 array.
        scheme: "symmetric" or "asymmetric".
        axis: If not None, compute per-channel along this axis.

    Returns:
        Tuple of (scale, zero_point).
    """
    if scheme not in ("symmetric", "asymmetric"):
        raise ValueError(f"scheme must be 'symmetric' or 'asymmetric', got '{scheme}'")

    if axis is not None:
        # Per-channel quantization
        reduce_axes = tuple(i for i in range(x.ndim) if i != axis)

        if scheme == "symmetric":
            abs_max = np.max(np.abs(x), axis=reduce_axes)
            abs_max = np.where(abs_max < 1e-10, 1.0, abs_max)
            scale = abs_max / 127.0
            zero_point = np.zeros(x.shape[axis], dtype=np.int32)
        else:
            x_min = np.min(x, axis=reduce_axes)
            x_max = np.max(x, axis=reduce_axes)
            data_range = x_max - x_min
            data_range = np.where(data_range < 1e-10, 1.0, data_range)
            scale = data_range / 255.0
            zero_point = np.round(-128.0 - x_min / scale).astype(np.int32)
            zero_point = np.clip(zero_point, -128, 127)
        return scale, zero_point

    # Per-tensor quantization
    if scheme == "symmetric":
        abs_max = float(np.max(np.abs(x)))
        if abs_max < 1e-10:
            return 1.0, 0
        scale = abs_max / 127.0
        return scale, 0

    # Asymmetric
    x_min = float(np.min(x))
    x_max = float(np.max(x))
    return compute_scale_zero_point(x_min, x_max, n_bits=8, scheme="asymmetric")


def quantize_int8(
    x: np.ndarray,
    scheme: str = "asymmetric",
    per_channel: bool = False,
    axis: int = 0,
) -> QuantizedTensor:
    """Quantize float32 tensor to int8.

    Formula (asymmetric):
        q = clamp(round(x / scale) + zero_point, -128, 127)

    Formula (symmetric):
        q = clamp(round(x / scale), -127, 127)

    Args:
        x: Input float32 numpy array.
        scheme: "symmetric" or "asymmetric".
        per_channel: If True, compute per-channel scale/zero_point.
        axis: Channel axis for per_channel quantization.

    Returns:
        QuantizedTensor with .data as int8 array.

    Raises:
        ValueError: If scheme is not "symmetric" or "asymmetric".
    """
    if scheme not in ("symmetric", "asymmetric"):
        raise ValueError(f"scheme must be 'symmetric' or 'asymmetric', got '{scheme}'")

    channel_axis = axis if per_channel else None
    scale, zero_point = compute_scale_zero_point_int8(x, scheme=scheme, axis=channel_axis)

    if per_channel and isinstance(scale, np.ndarray):
        # Reshape scale/zero_point for broadcasting
        shape = [1] * x.ndim
        shape[axis] = -1
        scale_broad = scale.reshape(shape)
        zp_broad = zero_point.reshape(shape)
    else:
        scale_broad = scale
        zp_broad = zero_point

    if scheme == "symmetric":
        q = np.round(x / scale_broad).astype(np.int32)
        q = np.clip(q, -127, 127).astype(np.int8)
    else:
        q = np.round(x / scale_broad).astype(np.int32) + zp_broad
        q = np.clip(q, -128, 127).astype(np.int8)

    return QuantizedTensor(
        data=q,
        scale=scale,
        zero_point=zero_point,
        scheme=scheme,
        original_dtype=x.dtype,
    )


def dequantize_int8(qt: QuantizedTensor) -> np.ndarray:
    """Reconstruct float32 from int8 quantized tensor.

    Formula (asymmetric):
        x_approx = (q - zero_point) * scale

    Formula (symmetric):
        x_approx = q * scale

    Args:
        qt: QuantizedTensor from quantize_int8.

    Returns:
        float32 numpy array approximating the original values.
    """
    q = qt.data.astype(np.float32)

    if qt.scheme == "symmetric":
        return q * qt.scale

    return (q - qt.zero_point) * qt.scale


class Int8Quantizer:
    """Stateful quantizer that calibrates scale/zero_point from data.

    Provides a calibrate-then-quantize workflow. If quantize() is called
    without prior calibration, it auto-calibrates from the input data.

    Args:
        scheme: "symmetric" or "asymmetric".
        per_channel: If True, compute per-channel parameters.
    """

    def __init__(self, scheme: str = "asymmetric", per_channel: bool = False) -> None:
        self.scheme = scheme
        self.per_channel = per_channel
        self.scale: float | np.ndarray | None = None
        self.zero_point: int | np.ndarray | None = None
        self._calibrated = False

    def calibrate(self, x: np.ndarray) -> Int8Quantizer:
        """Compute scale and zero_point from calibration data.

        Args:
            x: Representative calibration data.

        Returns:
            Self, for method chaining.
        """
        channel_axis = 0 if self.per_channel else None
        self.scale, self.zero_point = compute_scale_zero_point_int8(
            x, scheme=self.scheme, axis=channel_axis
        )
        self._calibrated = True
        return self

    def quantize(self, x: np.ndarray) -> QuantizedTensor:
        """Quantize using calibrated parameters.

        If not yet calibrated, auto-calibrates from input data.

        Args:
            x: Input float32 array.

        Returns:
            QuantizedTensor with int8 data.
        """
        if not self._calibrated:
            self.calibrate(x)
        return quantize_int8(x, scheme=self.scheme, per_channel=self.per_channel)

    def dequantize(self, qt: QuantizedTensor) -> np.ndarray:
        """Dequantize a QuantizedTensor back to float32.

        Args:
            qt: QuantizedTensor to dequantize.

        Returns:
            float32 numpy array.
        """
        return dequantize_int8(qt)
