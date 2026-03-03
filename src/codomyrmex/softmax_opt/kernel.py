import numpy as np


def softmax(x: np.ndarray, axis: int = -1, temperature: float = 1.0) -> np.ndarray:
    """
    Numerically stable softmax using max subtraction.

    Formula: softmax(x)_i = exp(x_i - max(x)) / sum(exp(x_j - max(x)))

    The max subtraction prevents overflow in exp() while not changing
    the mathematical result (since it cancels in numerator/denominator).

    # CUDA_ACCELERATE: Parallel reduction for max and sum

    Args:
        x: Input array
        axis: Axis to compute softmax over (default: last axis)
        temperature: Temperature scaling (higher = more uniform, lower = more peaked)

    Returns:
        Probability distribution with same shape as x, summing to 1 along axis
    """
    x_scaled = x / temperature
    x_max = np.max(x_scaled, axis=axis, keepdims=True)
    exp_x = np.exp(x_scaled - x_max)
    return exp_x / np.sum(exp_x, axis=axis, keepdims=True)


def log_softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    Numerically stable log-softmax using the log-sum-exp trick.

    log(softmax(x))_i = x_i - log(sum(exp(x_j)))
                       = x_i - max(x) - log(sum(exp(x_j - max(x))))

    Avoids computing softmax then taking log (loses numerical precision).
    Used in cross-entropy loss and KL divergence computations.
    """
    x_max = np.max(x, axis=axis, keepdims=True)
    shifted = x - x_max
    log_sum_exp = np.log(np.sum(np.exp(shifted), axis=axis, keepdims=True))
    return shifted - log_sum_exp


def online_softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    Online softmax using single-pass algorithm (Flash Attention style).

    Traditional softmax requires 2 passes (max, then sum).
    Online algorithm maintains running (max, sum*exp) in a single pass.

    This is the key insight behind Flash Attention's memory efficiency:
    you can compute softmax in tiles without storing the full attention matrix.

    Algorithm (1D):
        m = -inf, d = 0
        for each x_i:
            m_new = max(m, x_i)
            d_new = d * exp(m - m_new) + exp(x_i - m_new)
            m, d = m_new, d_new
        return exp(x - m) / d

    # CUDA_ACCELERATE: Tree reduction for parallel online softmax
    """
    x_flat = np.moveaxis(x, axis, -1).reshape(-1, x.shape[axis])

    result = np.zeros_like(x_flat)
    for row_idx in range(x_flat.shape[0]):
        row = x_flat[row_idx]
        m = float("-inf")
        d = 0.0

        # Single pass to compute max and normalizer
        for val in row:
            m_new = max(m, val)
            d = d * np.exp(m - m_new) + np.exp(val - m_new)
            m = m_new

        # Apply
        result[row_idx] = np.exp(row - m) / d

    # Restore shape
    result = result.reshape(*np.moveaxis(x, axis, -1).shape)
    return np.moveaxis(result, -1, axis)


def safe_softmax(x: np.ndarray, axis: int = -1, eps: float = 1e-8) -> np.ndarray:
    """
    Softmax with epsilon for numerical safety in attention masks.
    Adds epsilon to denominator to prevent division by zero.
    """
    x_max = np.max(x, axis=axis, keepdims=True)
    exp_x = np.exp(x - x_max)
    return exp_x / (np.sum(exp_x, axis=axis, keepdims=True) + eps)
