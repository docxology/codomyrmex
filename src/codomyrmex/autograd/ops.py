"""
Activation functions for the autograd engine.

Each function works with both ``Value`` (scalar) and ``Tensor`` objects,
returning the same type with a correctly wired backward function.
"""

from __future__ import annotations

import math
from typing import Union

import numpy as np

from .engine import Tensor, Value


def relu(x: Union[Value, Tensor]) -> Union[Value, Tensor]:
    """ReLU activation: max(0, x).

    Args:
        x: A Value or Tensor input.

    Returns:
        Same type as input with ReLU applied element-wise.
    """
    if isinstance(x, Value):
        return x.relu()

    # Tensor path
    out = Tensor(np.maximum(0.0, x.data), _children=(x,), _op="relu")

    def _backward() -> None:
        if x.grad is None:
            x.grad = np.zeros_like(x.data)
        x.grad += (out.data > 0).astype(np.float64) * out.grad

    out._backward = _backward
    return out


def tanh(x: Union[Value, Tensor]) -> Union[Value, Tensor]:
    """Hyperbolic tangent activation.

    Args:
        x: A Value or Tensor input.

    Returns:
        Same type as input with tanh applied element-wise.
    """
    if isinstance(x, Value):
        return x.tanh()

    # Tensor path
    t = np.tanh(x.data)
    out = Tensor(t, _children=(x,), _op="tanh")

    def _backward() -> None:
        if x.grad is None:
            x.grad = np.zeros_like(x.data)
        x.grad += (1.0 - t ** 2) * out.grad

    out._backward = _backward
    return out


def sigmoid(x: Union[Value, Tensor]) -> Union[Value, Tensor]:
    """Sigmoid activation: 1 / (1 + exp(-x)).

    Args:
        x: A Value or Tensor input.

    Returns:
        Same type as input with sigmoid applied element-wise.
    """
    if isinstance(x, Value):
        return x.sigmoid()

    # Tensor path
    s = 1.0 / (1.0 + np.exp(-x.data))
    out = Tensor(s, _children=(x,), _op="sigmoid")

    def _backward() -> None:
        if x.grad is None:
            x.grad = np.zeros_like(x.data)
        x.grad += s * (1.0 - s) * out.grad

    out._backward = _backward
    return out


def softmax(logits: Tensor) -> Tensor:
    """Numerically stable softmax for Tensor inputs.

    Applies softmax along the last axis.

    Args:
        logits: A Tensor of raw logits.

    Returns:
        Tensor with softmax probabilities and correct backward.
    """
    if isinstance(logits, Value):
        raise TypeError("softmax is only supported for Tensor inputs, not scalar Value")

    # Numerically stable: subtract max per row
    shifted = logits.data - np.max(logits.data, axis=-1, keepdims=True)
    exp_vals = np.exp(shifted)
    probs = exp_vals / np.sum(exp_vals, axis=-1, keepdims=True)
    out = Tensor(probs, _children=(logits,), _op="softmax")

    def _backward() -> None:
        if logits.grad is None:
            logits.grad = np.zeros_like(logits.data)
        # Jacobian-vector product for softmax
        # For each sample: dL/dx_i = sum_j (dL/dy_j * dy_j/dx_i)
        # dy_j/dx_i = y_j * (delta_ij - y_i)
        # Simplifies to: dL/dx = y * (dL/dy - sum(dL/dy * y))
        s = probs
        g = out.grad
        dot = np.sum(g * s, axis=-1, keepdims=True)
        logits.grad += s * (g - dot)

    out._backward = _backward
    return out
