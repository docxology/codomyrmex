"""
Autograd engine -- scalar Value and small Tensor automatic differentiation.

Implements reverse-mode automatic differentiation from scratch:
- Value: scalar autograd (Micrograd-style, Andrej Karpathy)
- Tensor: numpy-backed tensor autograd with gradient accumulation
"""

from __future__ import annotations

import math

import numpy as np

# ---------------------------------------------------------------------------
# Scalar Autograd: Value
# ---------------------------------------------------------------------------

class Value:
    """A scalar value that tracks its computation graph for reverse-mode autodiff.

    Every arithmetic operation on Value objects builds a DAG.  Calling
    ``backward()`` on the final node walks the DAG in reverse topological
    order and accumulates gradients via the chain rule.
    """

    __slots__ = ("data", "grad", "_backward", "_prev", "_op", "label")

    def __init__(
        self,
        data: float,
        _children: tuple[Value, ...] = (),
        _op: str = "",
        label: str = "",
    ) -> None:
        """Initialize a new Value node.

        Args:
            data: The scalar float value.
            _children: Tuple of parent nodes in the computation graph.
            _op: The operation that produced this node.
            label: An optional string label for debugging.
        """
        self.data = float(data)
        self.grad = 0.0
        self._backward = lambda: None
        self._prev = set(_children)
        self._op = _op
        self.label = label

    # -- forward ops --------------------------------------------------------

    def __add__(self, other: Value | float | int) -> Value:
        """Add two Values or a Value and a scalar."""
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), "+")

        def _backward() -> None:
            self.grad += out.grad
            other.grad += out.grad

        out._backward = _backward
        return out

    def __mul__(self, other: Value | float | int) -> Value:
        """Multiply two Values or a Value and a scalar."""
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")

        def _backward() -> None:
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad

        out._backward = _backward
        return out

    def __pow__(self, other: float | int) -> Value:
        """Raise a Value to a scalar power."""
        if isinstance(other, Value):
            raise NotImplementedError("Value**Value is not supported; use float exponent")
        out = Value(self.data ** other, (self,), f"**{other}")

        def _backward() -> None:
            self.grad += (other * self.data ** (other - 1)) * out.grad

        out._backward = _backward
        return out

    def __neg__(self) -> Value:
        """Negate a Value."""
        return self * -1

    def __sub__(self, other: Value | float | int) -> Value:
        """Subtract a Value or scalar from this Value."""
        return self + (-other if isinstance(other, Value) else Value(-other))

    def __truediv__(self, other: Value | float | int) -> Value:
        """Divide this Value by another Value or scalar."""
        return self * (other ** -1 if isinstance(other, Value) else Value(other) ** -1)

    def __radd__(self, other: float | int) -> Value:
        """Add a scalar to this Value (reflected)."""
        return self + other

    def __rmul__(self, other: float | int) -> Value:
        """Multiply a scalar by this Value (reflected)."""
        return self * other

    def __rsub__(self, other: float | int) -> Value:
        """Subtract this Value from a scalar (reflected)."""
        return Value(other) + (-self)

    def __rtruediv__(self, other: float | int) -> Value:
        """Divide a scalar by this Value (reflected)."""
        return Value(other) * (self ** -1)

    # -- special math -------------------------------------------------------

    def exp(self) -> Value:
        """Compute e^self with correct backward."""
        val = math.exp(self.data)
        out = Value(val, (self,), "exp")

        def _backward() -> None:
            self.grad += val * out.grad

        out._backward = _backward
        return out

    def tanh(self) -> Value:
        """Compute tanh(self) with correct backward."""
        t = math.tanh(self.data)
        out = Value(t, (self,), "tanh")

        def _backward() -> None:
            self.grad += (1 - t ** 2) * out.grad

        out._backward = _backward
        return out

    def relu(self) -> Value:
        """Compute max(0, self) with correct backward."""
        out = Value(max(0.0, self.data), (self,), "relu")

        def _backward() -> None:
            self.grad += (1.0 if out.data > 0 else 0.0) * out.grad

        out._backward = _backward
        return out

    def sigmoid(self) -> Value:
        """Compute 1/(1+exp(-self)) with correct backward."""
        s = 1.0 / (1.0 + math.exp(-self.data))
        out = Value(s, (self,), "sigmoid")

        def _backward() -> None:
            self.grad += s * (1.0 - s) * out.grad

        out._backward = _backward
        return out

    # -- backward -----------------------------------------------------------

    def backward(self) -> None:
        """Run reverse-mode autodiff through the computation graph.

        Builds a topological ordering of nodes reachable from *self*,
        then walks it in reverse, calling each node's ``_backward``.
        """
        topo: list[Value] = []
        visited: set[int] = set()

        def _build_topo(v: Value) -> None:
            vid = id(v)
            if vid not in visited:
                visited.add(vid)
                for child in v._prev:
                    _build_topo(child)
                topo.append(v)

        _build_topo(self)

        self.grad = 1.0
        for v in reversed(topo):
            v._backward()

    # -- repr ---------------------------------------------------------------

    def __repr__(self) -> str:
        """Return a string representation of the Value."""
        label_part = f", label={self.label!r}" if self.label else ""
        return f"Value(data={self.data:.6f}, grad={self.grad:.6f}{label_part})"


# ---------------------------------------------------------------------------
# Tensor Autograd
# ---------------------------------------------------------------------------

class Tensor:
    """A thin numpy-backed tensor with reverse-mode autodiff support.

    Each operation records parent tensors and a local backward function.
    Calling ``backward()`` on the final tensor propagates gradients back
    through the graph.
    """

    def __init__(
        self,
        data: list | np.ndarray,
        requires_grad: bool = False,
        _children: tuple[Tensor, ...] = (),
        _op: str = "",
    ) -> None:
        """Initialize a new Tensor node.

        Args:
            data: The tensor data as a list or numpy array.
            requires_grad: Whether this tensor requires gradients.
            _children: Tuple of parent nodes in the computation graph.
            _op: The operation that produced this node.
        """
        if isinstance(data, np.ndarray):
            self.data = data.astype(np.float64)
        else:
            self.data = np.array(data, dtype=np.float64)
        self.requires_grad = requires_grad
        self.grad: np.ndarray | None = None
        self._backward = lambda: None
        self._prev = set(_children)
        self._op = _op
        self.shape = self.data.shape

    # -- forward ops --------------------------------------------------------

    def __add__(self, other: Tensor | float | int | np.ndarray) -> Tensor:
        """Add two Tensors or a Tensor and a scalar/array."""
        other = other if isinstance(other, Tensor) else Tensor(np.asarray(other))
        out = Tensor(self.data + other.data, _children=(self, other), _op="+")

        def _backward() -> None:
            if self.grad is None:
                self.grad = np.zeros_like(self.data)
            if other.grad is None:
                other.grad = np.zeros_like(other.data)
            # Handle broadcasting: sum over broadcasted dims
            self_grad = out.grad
            other_grad = out.grad
            if self.data.shape != out.grad.shape:
                self_grad = _unbroadcast(out.grad, self.data.shape)
            if other.data.shape != out.grad.shape:
                other_grad = _unbroadcast(out.grad, other.data.shape)
            self.grad += self_grad
            other.grad += other_grad

        out._backward = _backward
        return out

    def __mul__(self, other: Tensor | float | int | np.ndarray) -> Tensor:
        """Multiply two Tensors or a Tensor and a scalar/array element-wise."""
        other = other if isinstance(other, Tensor) else Tensor(np.asarray(other))
        out = Tensor(self.data * other.data, _children=(self, other), _op="*")

        def _backward() -> None:
            if self.grad is None:
                self.grad = np.zeros_like(self.data)
            if other.grad is None:
                other.grad = np.zeros_like(other.data)
            sg = other.data * out.grad
            og = self.data * out.grad
            if self.data.shape != sg.shape:
                sg = _unbroadcast(sg, self.data.shape)
            if other.data.shape != og.shape:
                og = _unbroadcast(og, other.data.shape)
            self.grad += sg
            other.grad += og

        out._backward = _backward
        return out

    def __matmul__(self, other: Tensor) -> Tensor:
        """Matrix multiply two Tensors."""
        out = Tensor(self.data @ other.data, _children=(self, other), _op="@")

        def _backward() -> None:
            if self.grad is None:
                self.grad = np.zeros_like(self.data)
            if other.grad is None:
                other.grad = np.zeros_like(other.data)
            self.grad += out.grad @ other.data.T
            other.grad += self.data.T @ out.grad

        out._backward = _backward
        return out

    def __neg__(self) -> Tensor:
        """Negate a Tensor."""
        return self * -1.0

    def __sub__(self, other: Tensor | float | int | np.ndarray) -> Tensor:
        """Subtract a Tensor or scalar/array from this Tensor."""
        other = other if isinstance(other, Tensor) else Tensor(np.asarray(other))
        return self + (other * -1.0)

    def __radd__(self, other: float | int) -> Tensor:
        """Add a scalar to this Tensor (reflected)."""
        return self + other

    def __rmul__(self, other: float | int) -> Tensor:
        """Multiply a scalar by this Tensor (reflected)."""
        return self * other

    # -- reductions ---------------------------------------------------------

    def sum(self, axis: int | None = None, keepdims: bool = False) -> Tensor:
        """Sum elements along an axis (or all elements)."""
        result = np.sum(self.data, axis=axis, keepdims=keepdims)
        out = Tensor(result, _children=(self,), _op="sum")

        def _backward() -> None:
            if self.grad is None:
                self.grad = np.zeros_like(self.data)
            if out.grad.shape == ():
                self.grad += np.ones_like(self.data) * float(out.grad)
            else:
                grad = out.grad
                if not keepdims and axis is not None:
                    grad = np.expand_dims(grad, axis=axis)
                self.grad += np.broadcast_to(grad, self.data.shape).copy()

        out._backward = _backward
        return out

    def mean(self, axis: int | None = None, keepdims: bool = False) -> Tensor:
        """Mean of elements along an axis (or all elements)."""
        result = np.mean(self.data, axis=axis, keepdims=keepdims)
        out = Tensor(result, _children=(self,), _op="mean")
        n = self.data.size if axis is None else self.data.shape[axis]

        def _backward() -> None:
            if self.grad is None:
                self.grad = np.zeros_like(self.data)
            if out.grad.shape == ():
                self.grad += np.ones_like(self.data) * float(out.grad) / n
            else:
                grad = out.grad
                if not keepdims and axis is not None:
                    grad = np.expand_dims(grad, axis=axis)
                self.grad += np.broadcast_to(grad / n, self.data.shape).copy()

        out._backward = _backward
        return out

    def reshape(self, *shape: int) -> Tensor:
        """Reshape tensor data, preserving gradient flow."""
        original_shape = self.data.shape
        out = Tensor(self.data.reshape(shape), _children=(self,), _op="reshape")

        def _backward() -> None:
            if self.grad is None:
                self.grad = np.zeros_like(self.data)
            self.grad += out.grad.reshape(original_shape)

        out._backward = _backward
        return out

    # -- backward -----------------------------------------------------------

    def backward(self, grad: np.ndarray | None = None) -> None:
        """Run reverse-mode autodiff through the tensor computation graph."""
        topo: list[Tensor] = []
        visited: set[int] = set()

        def _build_topo(t: Tensor) -> None:
            tid = id(t)
            if tid not in visited:
                visited.add(tid)
                for child in t._prev:
                    _build_topo(child)
                topo.append(t)

        _build_topo(self)

        if grad is not None:
            self.grad = grad.copy()
        else:
            self.grad = np.ones_like(self.data)

        for t in reversed(topo):
            t._backward()

    # -- repr ---------------------------------------------------------------

    def __repr__(self) -> str:
        """Return a string representation of the Tensor."""
        return f"Tensor(shape={self.shape}, data={self.data})"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _unbroadcast(grad: np.ndarray, target_shape: tuple[int, ...]) -> np.ndarray:
    """Sum out dimensions that were broadcast to match *target_shape*.

    Args:
        grad: The gradient array to unbroadcast.
        target_shape: The original shape before broadcasting.

    Returns:
        The unbroadcasted gradient array matching target_shape.
    """
    # Pad target_shape with leading 1s to match grad ndim
    ndim_diff = grad.ndim - len(target_shape)
    padded = (1,) * ndim_diff + target_shape

    # Sum over axes that were broadcast (size-1 in target or added)
    axes_to_sum = []
    for i, (g, t) in enumerate(zip(grad.shape, padded, strict=False)):
        if t == 1 and g != 1:
            axes_to_sum.append(i)
        elif t != g:
            axes_to_sum.append(i)

    if axes_to_sum:
        grad = grad.sum(axis=tuple(axes_to_sum), keepdims=True)

    # Remove leading dims that were added by broadcasting
    if ndim_diff > 0:
        grad = grad.reshape(target_shape)
    elif grad.shape != target_shape:
        grad = grad.reshape(target_shape)

    return grad
