"""Quantization utility functions.

Provides scale/zero-point computation, per-channel scaling,
and quantization error metrics for evaluating reconstruction quality.
"""

from __future__ import annotations

import numpy as np


def compute_scale_zero_point(
    x_min: float,
    x_max: float,
    n_bits: int = 8,
    scheme: str = "asymmetric",
) -> tuple[float, int]:
    """Compute scale and zero_point for n-bit quantization.

    Args:
        x_min: Minimum value of the data range.
        x_max: Maximum value of the data range.
        n_bits: Number of bits for quantization (default 8).
        scheme: "asymmetric" or "symmetric".

    Returns:
        Tuple of (scale, zero_point).

    Raises:
        ValueError: If scheme is not "asymmetric" or "symmetric".
    """
    if scheme not in ("asymmetric", "symmetric"):
        raise ValueError(f"scheme must be 'asymmetric' or 'symmetric', got '{scheme}'")

    if scheme == "symmetric":
        abs_max = max(abs(x_min), abs(x_max))
        qmax = (1 << (n_bits - 1)) - 1  # 127 for 8-bit
        if abs_max < 1e-10:
            return 1.0, 0
        scale = float(abs_max / qmax)
        return scale, 0

    # asymmetric
    qmin = -(1 << (n_bits - 1))  # -128 for 8-bit
    qmax = (1 << (n_bits - 1)) - 1  # 127 for 8-bit
    n_levels = qmax - qmin  # 255 for 8-bit

    if (x_max - x_min) < 1e-10:
        return 1.0, 0

    scale = float((x_max - x_min) / n_levels)
    zero_point = round(qmin - x_min / scale)
    zero_point = max(qmin, min(qmax, zero_point))

    return scale, zero_point


def per_channel_scale(x: np.ndarray, axis: int = 0) -> np.ndarray:
    """Compute per-channel max absolute value for scale computation.

    For a 2D tensor with axis=0, returns one scale per row.
    For axis=1, returns one scale per column.

    Args:
        x: Input array.
        axis: Channel axis along which to compute per-channel max abs.

    Returns:
        1D array of max absolute values, one per channel.
    """
    # Compute max absolute value along the non-channel axes
    reduce_axes = tuple(i for i in range(x.ndim) if i != axis)
    if len(reduce_axes) == 0:
        return np.abs(x)
    return np.max(np.abs(x), axis=reduce_axes)


def quantization_error(original: np.ndarray, reconstructed: np.ndarray) -> dict:
    """Compute quantization error metrics.

    Args:
        original: The original float tensor.
        reconstructed: The dequantized (reconstructed) tensor.

    Returns:
        Dictionary with keys:
            - max_abs_error: Maximum absolute error.
            - mean_abs_error: Mean absolute error.
            - relative_error: Mean absolute error relative to mean absolute value.
            - snr_db: Signal-to-noise ratio in decibels.
    """
    diff = original.astype(np.float64) - reconstructed.astype(np.float64)
    original_f64 = original.astype(np.float64)

    max_abs_err = float(np.max(np.abs(diff)))
    mean_abs_err = float(np.mean(np.abs(diff)))
    mean_abs_orig = float(np.mean(np.abs(original_f64)))
    relative_err = float(mean_abs_err / (mean_abs_orig + 1e-8))

    signal_power = float(np.mean(original_f64**2))
    noise_power = float(np.mean(diff**2))
    snr = float(10.0 * np.log10(signal_power / (noise_power + 1e-10)))

    return {
        "max_abs_error": max_abs_err,
        "mean_abs_error": mean_abs_err,
        "relative_error": relative_err,
        "snr_db": snr,
    }
