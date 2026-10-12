"""Real NumPy controls for reduction gradients across supported type profiles."""

import numpy as np
import pytest

from codomyrmex.autograd.engine import Tensor


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["sum", "mean"])
@pytest.mark.parametrize("axis", [None, 0, 1, -1])
@pytest.mark.parametrize("keepdims", [False, True])
def test_weighted_reduction_backward(operation, axis, keepdims):
    """A non-unit upstream derivative must reach every reduced element."""
    values = np.arange(1.0, 7.0).reshape(2, 3)
    tensor = Tensor(values)
    reduced = getattr(tensor, operation)(axis=axis, keepdims=keepdims)
    loss = (reduced * 2.5).sum()
    loss.backward()
    divisor = (
        1
        if operation == "sum"
        else (values.size if axis is None else values.shape[axis])
    )
    assert tensor.grad is not None
    np.testing.assert_allclose(tensor.grad, np.full_like(values, 2.5 / divisor))


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["sum", "mean"])
def test_missing_upstream_gradient_fails_before_mutation(operation):
    """An unseeded closure cannot silently invent a gradient."""
    tensor = Tensor([[1.0, 2.0], [3.0, 4.0]])
    reduced = getattr(tensor, operation)(axis=0)
    with pytest.raises(RuntimeError, match="requires an output gradient"):
        reduced._backward()
    assert tensor.grad is None
    assert reduced.grad is None
