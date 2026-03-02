"""Activation functions implemented from scratch with NumPy."""
import numpy as np


def gelu(x: np.ndarray) -> np.ndarray:
    """Gaussian Error Linear Unit (GELU activation, Hendrycks & Gimpel 2016).

    Approximation: 0.5 * x * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
    """
    return 0.5 * x * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (x + 0.044715 * x**3)))


def relu(x: np.ndarray) -> np.ndarray:
    """Rectified Linear Unit: max(0, x)."""
    return np.maximum(0.0, x)


def swish(x: np.ndarray) -> np.ndarray:
    """Swish activation: x * sigmoid(x) (Ramachandran et al. 2017)."""
    return x * (1.0 / (1.0 + np.exp(-x)))
