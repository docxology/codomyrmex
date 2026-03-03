"""Model merging utilities: SLERP, linear interpolation, and model soups."""

import numpy as np


def slerp(
    v0: np.ndarray,
    v1: np.ndarray,
    t: float,
    eps: float = 1e-8,
) -> np.ndarray:
    """
    Spherical Linear Interpolation (SLERP) between two vectors.

    SLERP interpolates along the arc of a sphere, preserving vector magnitude
    better than linear interpolation for unit vectors (weight tensors on a hypersphere).

    Formula:
        slerp(v0, v1, t) = sin((1-t)*omega)/sin(omega) * v0 + sin(t*omega)/sin(omega) * v1
    where omega = arccos(v0 dot v1 / (|v0|*|v1|))

    Falls back to linear interpolation when vectors are nearly parallel (sin(omega) near 0).

    Args:
        v0: Start vector (any shape)
        v1: End vector (same shape as v0)
        t: Interpolation parameter in [0, 1] (0=v0, 1=v1)
        eps: Numerical stability epsilon

    Returns:
        Interpolated vector with same shape as v0
    """
    v0_flat = v0.flatten().astype(np.float64)
    v1_flat = v1.flatten().astype(np.float64)

    # Normalize
    v0_norm = v0_flat / (np.linalg.norm(v0_flat) + eps)
    v1_norm = v1_flat / (np.linalg.norm(v1_flat) + eps)

    # Angle between vectors
    dot = np.clip(np.dot(v0_norm, v1_norm), -1.0, 1.0)
    omega = np.arccos(abs(dot))

    if abs(np.sin(omega)) < eps:
        # Nearly parallel: fall back to linear interpolation
        result = (1 - t) * v0_flat + t * v1_flat
    else:
        coeff0 = np.sin((1 - t) * omega) / np.sin(omega)
        coeff1 = np.sin(t * omega) / np.sin(omega)
        result = coeff0 * v0_flat + coeff1 * v1_flat

    # Preserve original magnitude via linear interpolation of norms
    target_norm = (1 - t) * np.linalg.norm(v0_flat) + t * np.linalg.norm(v1_flat)
    result_norm = np.linalg.norm(result)
    if result_norm > eps:
        result = result * (target_norm / result_norm)

    return result.reshape(v0.shape)


def linear_interpolate(
    params_a: dict[str, np.ndarray],
    params_b: dict[str, np.ndarray],
    alpha: float = 0.5,
) -> dict[str, np.ndarray]:
    """
    Linear interpolation between two model parameter dicts.
    W_merged = (1-alpha) * W_a + alpha * W_b
    """
    merged = {}
    for key in params_a:
        if key in params_b:
            merged[key] = (1 - alpha) * params_a[key] + alpha * params_b[key]
        else:
            merged[key] = params_a[key].copy()
    return merged


def model_soup(
    param_dicts: list[dict[str, np.ndarray]],
    weights: list[float] | None = None,
) -> dict[str, np.ndarray]:
    """
    Model Soup (Wortsman et al. 2022): weighted average of model parameters.

    Model soups of fine-tuned models from the same base often outperform
    individual models by smoothing out loss basin differences.

    Args:
        param_dicts: List of parameter dictionaries from multiple models
        weights: Optional weights for weighted average (uniform if None)

    Returns:
        Averaged parameter dict
    """
    if not param_dicts:
        raise ValueError("Need at least one model")

    n = len(param_dicts)
    if weights is None:
        weights = [1.0 / n] * n
    else:
        total = sum(weights)
        weights = [w / total for w in weights]

    result = {}
    for key in param_dicts[0]:
        arrays = [p[key] for p in param_dicts if key in p]
        w_vals = [weights[i] for i in range(len(param_dicts)) if key in param_dicts[i]]

        stacked = np.stack(arrays)
        w_arr = np.array(w_vals)
        # Reshape weights for broadcasting: (n_models, 1, 1, ...) to match param dims
        w_shaped = w_arr.reshape(-1, *([1] * (stacked.ndim - 1)))
        result[key] = np.sum(stacked * w_shaped, axis=0)

    return result


class ModelMerger:
    """High-level model merging interface."""

    def __init__(self, method: str = "slerp"):
        self.method = method

    def merge(
        self,
        params_a: dict[str, np.ndarray],
        params_b: dict[str, np.ndarray],
        alpha: float = 0.5,
    ) -> dict[str, np.ndarray]:
        """Merge two models using the configured method."""
        if self.method == "slerp":
            merged = {}
            for key in params_a:
                if key in params_b:
                    merged[key] = slerp(params_a[key], params_b[key], alpha)
                else:
                    merged[key] = params_a[key].copy()
            return merged
        elif self.method == "linear":
            return linear_interpolate(params_a, params_b, alpha)
        else:
            raise ValueError(f"Unknown merge method: {self.method}")
