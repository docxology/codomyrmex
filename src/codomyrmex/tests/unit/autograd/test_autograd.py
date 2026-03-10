"""
Unit tests for the autograd engine.

Tests cover:
- Value scalar forward and backward passes
- Chain rule correctness
- Numerical gradient verification
- Tensor operations (add, matmul, sum, mean)
- Activation functions (relu, tanh, sigmoid, softmax)
- MCP tool interface
"""

import math

import numpy as np
import pytest

from codomyrmex.autograd import Tensor, Value, relu, sigmoid, softmax, tanh

# ---------------------------------------------------------------------------
# Value (scalar autograd)
# ---------------------------------------------------------------------------


class TestValueForward:
    """Forward-pass correctness for scalar Value operations."""

    @pytest.mark.unit
    def test_add_forward(self):
        a = Value(2.0)
        b = Value(3.0)
        c = a + b
        assert c.data == 5.0

    @pytest.mark.unit
    def test_mul_forward(self):
        a = Value(4.0)
        b = Value(5.0)
        c = a * b
        assert c.data == 20.0

    @pytest.mark.unit
    def test_pow_forward(self):
        a = Value(3.0)
        c = a**2
        assert c.data == 9.0

    @pytest.mark.unit
    def test_pow_negative_exponent(self):
        a = Value(2.0)
        c = a**-1
        assert abs(c.data - 0.5) < 1e-9

    @pytest.mark.unit
    def test_pow_fractional_exponent(self):
        a = Value(9.0)
        c = a**0.5
        assert abs(c.data - 3.0) < 1e-9

    @pytest.mark.unit
    def test_neg_forward(self):
        a = Value(7.0)
        b = -a
        assert b.data == -7.0

    @pytest.mark.unit
    def test_sub_forward(self):
        a = Value(10.0)
        b = Value(3.0)
        c = a - b
        assert c.data == 7.0

    @pytest.mark.unit
    def test_div_forward(self):
        a = Value(10.0)
        b = Value(4.0)
        c = a / b
        assert abs(c.data - 2.5) < 1e-9

    @pytest.mark.unit
    def test_radd_forward(self):
        a = Value(3.0)
        c = 5.0 + a
        assert c.data == 8.0

    @pytest.mark.unit
    def test_rmul_forward(self):
        a = Value(3.0)
        c = 2.0 * a
        assert c.data == 6.0

    @pytest.mark.unit
    def test_rsub_forward(self):
        a = Value(3.0)
        c = 10.0 - a
        assert c.data == 7.0

    @pytest.mark.unit
    def test_rtruediv_forward(self):
        a = Value(4.0)
        c = 8.0 / a
        assert abs(c.data - 2.0) < 1e-9

    @pytest.mark.unit
    def test_exp_forward(self):
        a = Value(1.0)
        c = a.exp()
        assert abs(c.data - math.e) < 1e-9

    @pytest.mark.unit
    def test_repr(self):
        a = Value(3.14, label="pi")
        r = repr(a)
        assert "3.14" in r
        assert "pi" in r


class TestValueBackward:
    """Backward-pass correctness for scalar Value operations."""

    @pytest.mark.unit
    def test_add_backward(self):
        a = Value(2.0, label="a")
        b = Value(3.0, label="b")
        c = a + b
        c.backward()
        assert a.grad == 1.0
        assert b.grad == 1.0

    @pytest.mark.unit
    def test_mul_backward(self):
        a = Value(2.0, label="a")
        b = Value(3.0, label="b")
        c = a * b
        c.backward()
        assert a.grad == 3.0  # dc/da = b = 3
        assert b.grad == 2.0  # dc/db = a = 2

    @pytest.mark.unit
    def test_pow_backward(self):
        a = Value(3.0)
        c = a**3
        c.backward()
        # d(x^3)/dx = 3x^2 = 27
        assert abs(a.grad - 27.0) < 1e-9

    @pytest.mark.unit
    def test_pow_negative_backward(self):
        a = Value(2.0)
        c = a**-1  # 1/x
        c.backward()
        # d(1/x)/dx = -1/x^2 = -1/4 = -0.25
        assert abs(a.grad - (-0.25)) < 1e-9

    @pytest.mark.unit
    def test_chain_rule(self):
        # f(x) = (x+1)^2, f'(x) = 2(x+1)
        x = Value(3.0)
        f = (x + Value(1.0)) ** 2
        f.backward()
        assert abs(x.grad - 8.0) < 1e-6  # 2*(3+1) = 8

    @pytest.mark.unit
    def test_complex_expression(self):
        # f(a,b) = a*b + a^2, df/da = b + 2a, df/db = a
        a = Value(2.0)
        b = Value(3.0)
        f = a * b + a**2
        f.backward()
        assert abs(a.grad - 7.0) < 1e-9  # 3 + 2*2 = 7
        assert abs(b.grad - 2.0) < 1e-9  # 2

    @pytest.mark.unit
    def test_shared_node_gradient_accumulation(self):
        # f(x) = x + x = 2x, df/dx = 2
        x = Value(5.0)
        f = x + x
        f.backward()
        assert abs(x.grad - 2.0) < 1e-9

    @pytest.mark.unit
    def test_exp_backward(self):
        x = Value(1.0)
        y = x.exp()
        y.backward()
        # d(e^x)/dx = e^x = e
        assert abs(x.grad - math.e) < 1e-6

    @pytest.mark.unit
    def test_div_backward(self):
        # f(a,b) = a/b, df/da = 1/b, df/db = -a/b^2
        a = Value(6.0)
        b = Value(3.0)
        f = a / b
        f.backward()
        assert abs(a.grad - 1.0 / 3.0) < 1e-6
        assert abs(b.grad - (-6.0 / 9.0)) < 1e-6

    @pytest.mark.unit
    def test_neg_backward(self):
        x = Value(4.0)
        y = -x
        y.backward()
        assert abs(x.grad - (-1.0)) < 1e-9

    @pytest.mark.unit
    def test_deep_chain(self):
        # f(x) = ((x * 2 + 1) ** 2 - 3) * 0.5
        x = Value(1.0)
        f = ((x * 2 + 1) ** 2 - 3) * 0.5
        f.backward()
        # f(x) = 0.5 * ((2x+1)^2 - 3)
        # f'(x) = 0.5 * 2*(2x+1)*2 = 2*(2x+1) = 2*3 = 6
        assert abs(x.grad - 6.0) < 1e-6


class TestActivationsScalar:
    """Activation functions on scalar Value."""

    @pytest.mark.unit
    def test_relu_positive(self):
        x = Value(3.0)
        y = relu(x)
        assert y.data == 3.0
        y.backward()
        assert x.grad == 1.0

    @pytest.mark.unit
    def test_relu_negative(self):
        x = Value(-2.0)
        y = relu(x)
        assert y.data == 0.0
        y.backward()
        assert x.grad == 0.0

    @pytest.mark.unit
    def test_tanh_zero(self):
        x = Value(0.0)
        y = tanh(x)
        assert abs(y.data) < 1e-9
        y.backward()
        # tanh'(0) = 1 - tanh(0)^2 = 1
        assert abs(x.grad - 1.0) < 1e-6

    @pytest.mark.unit
    def test_tanh_backward(self):
        x = Value(0.0)
        y = tanh(x)
        y.backward()
        assert abs(x.grad - 1.0) < 1e-6

    @pytest.mark.unit
    def test_sigmoid_zero(self):
        x = Value(0.0)
        y = sigmoid(x)
        assert abs(y.data - 0.5) < 1e-9
        y.backward()
        # sigmoid'(0) = 0.5 * 0.5 = 0.25
        assert abs(x.grad - 0.25) < 1e-6

    @pytest.mark.unit
    def test_sigmoid_large_positive(self):
        x = Value(10.0)
        y = sigmoid(x)
        assert y.data > 0.999

    @pytest.mark.unit
    def test_gradient_check_numerical(self):
        """Numerical gradient should match analytic gradient."""
        eps = 1e-5

        def f(v):
            return tanh(Value(v) * Value(2.0) + Value(1.0))

        # Numerical gradient
        y_plus = f(1.5 + eps)
        y_minus = f(1.5 - eps)
        numerical_grad = (y_plus.data - y_minus.data) / (2 * eps)

        # Analytic gradient
        x_a = Value(1.5)
        out = tanh(x_a * Value(2.0) + Value(1.0))
        out.backward()
        analytic_grad = x_a.grad

        assert abs(analytic_grad - numerical_grad) < 1e-4


# ---------------------------------------------------------------------------
# Tensor operations
# ---------------------------------------------------------------------------


class TestTensorForward:
    """Forward-pass correctness for Tensor operations."""

    @pytest.mark.unit
    def test_tensor_add(self):
        a = Tensor([1.0, 2.0, 3.0])
        b = Tensor([4.0, 5.0, 6.0])
        c = a + b
        np.testing.assert_allclose(c.data, [5.0, 7.0, 9.0])

    @pytest.mark.unit
    def test_tensor_mul(self):
        a = Tensor([2.0, 3.0])
        b = Tensor([4.0, 5.0])
        c = a * b
        np.testing.assert_allclose(c.data, [8.0, 15.0])

    @pytest.mark.unit
    def test_tensor_matmul(self):
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = Tensor([[5.0, 6.0], [7.0, 8.0]])
        c = a @ b
        expected = np.array([[19.0, 22.0], [43.0, 50.0]])
        np.testing.assert_allclose(c.data, expected)

    @pytest.mark.unit
    def test_tensor_neg(self):
        a = Tensor([1.0, -2.0, 3.0])
        b = -a
        np.testing.assert_allclose(b.data, [-1.0, 2.0, -3.0])

    @pytest.mark.unit
    def test_tensor_sub(self):
        a = Tensor([5.0, 6.0])
        b = Tensor([1.0, 2.0])
        c = a - b
        np.testing.assert_allclose(c.data, [4.0, 4.0])

    @pytest.mark.unit
    def test_tensor_sum(self):
        a = Tensor([1.0, 2.0, 3.0])
        s = a.sum()
        assert abs(s.data - 6.0) < 1e-9

    @pytest.mark.unit
    def test_tensor_mean(self):
        a = Tensor([2.0, 4.0, 6.0])
        m = a.mean()
        assert abs(m.data - 4.0) < 1e-9

    @pytest.mark.unit
    def test_tensor_reshape(self):
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = a.reshape(4)
        np.testing.assert_allclose(b.data, [1.0, 2.0, 3.0, 4.0])

    @pytest.mark.unit
    def test_tensor_scalar_add(self):
        a = Tensor([1.0, 2.0])
        c = a + 3.0
        np.testing.assert_allclose(c.data, [4.0, 5.0])

    @pytest.mark.unit
    def test_tensor_scalar_mul(self):
        a = Tensor([2.0, 3.0])
        c = a * 2.0
        np.testing.assert_allclose(c.data, [4.0, 6.0])

    @pytest.mark.unit
    def test_tensor_radd(self):
        a = Tensor([1.0, 2.0])
        c = 5.0 + a
        np.testing.assert_allclose(c.data, [6.0, 7.0])

    @pytest.mark.unit
    def test_tensor_rmul(self):
        a = Tensor([3.0, 4.0])
        c = 2.0 * a
        np.testing.assert_allclose(c.data, [6.0, 8.0])

    @pytest.mark.unit
    def test_tensor_sum_axis(self):
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        s0 = a.sum(axis=0)
        s1 = a.sum(axis=1)
        np.testing.assert_allclose(s0.data, [4.0, 6.0])
        np.testing.assert_allclose(s1.data, [3.0, 7.0])

    @pytest.mark.unit
    def test_tensor_mean_axis(self):
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        m0 = a.mean(axis=0)
        m1 = a.mean(axis=1)
        np.testing.assert_allclose(m0.data, [2.0, 3.0])
        np.testing.assert_allclose(m1.data, [1.5, 3.5])

    @pytest.mark.unit
    def test_tensor_repr(self):
        a = Tensor([1.0, 2.0])
        r = repr(a)
        assert "Tensor" in r
        assert "shape" in r


class TestTensorBackward:
    """Backward-pass correctness for Tensor operations."""

    @pytest.mark.unit
    def test_add_backward(self):
        a = Tensor([1.0, 2.0])
        b = Tensor([3.0, 4.0])
        c = a + b
        s = c.sum()
        s.backward()
        np.testing.assert_allclose(a.grad, [1.0, 1.0])  # type: ignore
        np.testing.assert_allclose(b.grad, [1.0, 1.0])  # type: ignore

    @pytest.mark.unit
    def test_mul_backward(self):
        a = Tensor([2.0, 3.0])
        b = Tensor([4.0, 5.0])
        c = a * b
        s = c.sum()
        s.backward()
        # ds/da_i = b_i
        np.testing.assert_allclose(a.grad, [4.0, 5.0])  # type: ignore
        np.testing.assert_allclose(b.grad, [2.0, 3.0])  # type: ignore

    @pytest.mark.unit
    def test_matmul_backward(self):
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = Tensor([[1.0, 0.0], [0.0, 1.0]])  # identity
        c = a @ b
        s = c.sum()
        s.backward()
        # d(sum(A@I))/dA = ones @ I^T = ones
        np.testing.assert_allclose(a.grad, np.ones((2, 2)))  # type: ignore

    @pytest.mark.unit
    def test_sum_backward(self):
        a = Tensor([1.0, 2.0, 3.0])
        s = a.sum()
        s.backward()
        np.testing.assert_allclose(a.grad, [1.0, 1.0, 1.0])  # type: ignore

    @pytest.mark.unit
    def test_sum_axis_backward(self):
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        s = a.sum(axis=0)
        # s is [4, 6]
        # loss = sum(s) = sum(a)
        loss = s.sum()
        loss.backward()
        np.testing.assert_allclose(a.grad, np.ones((2, 2)))  # type: ignore

    @pytest.mark.unit
    def test_mean_backward(self):
        a = Tensor([2.0, 4.0, 6.0])
        m = a.mean()
        m.backward()
        np.testing.assert_allclose(a.grad, [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0])  # type: ignore

    @pytest.mark.unit
    def test_mean_axis_backward(self):
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        m = a.mean(axis=1)
        # m is [1.5, 3.5]
        # loss = m.sum() = (a[0,0]+a[0,1])/2 + (a[1,0]+a[1,1])/2
        loss = m.sum()
        loss.backward()
        np.testing.assert_allclose(a.grad, np.ones((2, 2)) * 0.5)  # type: ignore

    @pytest.mark.unit
    def test_broadcasting_add_backward(self):
        # Matrix + Row Vector
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = Tensor([10.0, 20.0])
        c = a + b  # [[11, 22], [13, 24]]
        s = c.sum()
        s.backward()
        np.testing.assert_allclose(a.grad, np.ones((2, 2)))  # type: ignore
        np.testing.assert_allclose(b.grad, [2.0, 2.0])  # type: ignore

    @pytest.mark.unit
    def test_broadcasting_mul_backward(self):
        # Matrix * Column Vector
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = Tensor([[10.0], [20.0]])
        c = a * b  # [[10, 20], [60, 80]]
        s = c.sum()
        s.backward()
        # dc/da = b (broadcasted)
        np.testing.assert_allclose(a.grad, [[10.0, 10.0], [20.0, 20.0]])  # type: ignore
        # dc/db = sum(a, axis=1, keepdims=True)
        np.testing.assert_allclose(b.grad, [[3.0], [7.0]])  # type: ignore

    @pytest.mark.unit
    def test_reshape_backward(self):
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = a.reshape(4)
        s = b.sum()
        s.backward()
        np.testing.assert_allclose(a.grad, np.ones((2, 2)))  # type: ignore

    @pytest.mark.unit
    def test_chain_tensor(self):
        # f(a) = sum((a * 2 + 1))
        a = Tensor([1.0, 2.0, 3.0])
        f = (a * 2.0 + 1.0).sum()
        f.backward()
        # df/da_i = 2
        np.testing.assert_allclose(a.grad, [2.0, 2.0, 2.0])  # type: ignore


class TestActivationsTensor:
    """Activation functions on Tensor objects."""

    @pytest.mark.unit
    def test_relu_tensor(self):
        a = Tensor([-1.0, 0.0, 1.0, 2.0])
        b = relu(a)
        np.testing.assert_allclose(b.data, [0.0, 0.0, 1.0, 2.0])
        s = b.sum()
        s.backward()
        np.testing.assert_allclose(a.grad, [0.0, 0.0, 1.0, 1.0])  # type: ignore

    @pytest.mark.unit
    def test_tanh_tensor(self):
        a = Tensor([0.0])
        b = tanh(a)
        np.testing.assert_allclose(b.data, [0.0], atol=1e-9)
        s = b.sum()
        s.backward()
        np.testing.assert_allclose(a.grad, [1.0], atol=1e-6)  # type: ignore

    @pytest.mark.unit
    def test_sigmoid_tensor(self):
        a = Tensor([0.0])
        b = sigmoid(a)
        np.testing.assert_allclose(b.data, [0.5], atol=1e-9)
        s = b.sum()
        s.backward()
        np.testing.assert_allclose(a.grad, [0.25], atol=1e-6)  # type: ignore

    @pytest.mark.unit
    def test_softmax_forward(self):
        logits = Tensor([1.0, 2.0, 3.0])
        probs = softmax(logits)
        # Sum of softmax should be 1
        assert abs(np.sum(probs.data) - 1.0) < 1e-9
        # Largest logit should have largest probability
        assert probs.data[2] > probs.data[1] > probs.data[0]

    @pytest.mark.unit
    def test_softmax_numerical_stability(self):
        # Large logits should not cause overflow
        logits = Tensor([1000.0, 1001.0, 1002.0])
        probs = softmax(logits)
        assert abs(np.sum(probs.data) - 1.0) < 1e-9
        assert not np.any(np.isnan(probs.data))
        assert not np.any(np.isinf(probs.data))

    @pytest.mark.unit
    def test_softmax_backward(self):
        logits = Tensor([1.0, 2.0, 3.0])
        probs = softmax(logits)
        # Use a specific element as loss
        loss = probs.sum()
        loss.backward()
        # Sum of softmax is always 1, so gradient of sum w.r.t. logits is 0
        np.testing.assert_allclose(logits.grad, np.zeros(3), atol=1e-9)  # type: ignore

    @pytest.mark.unit
    def test_softmax_rejects_value(self):
        with pytest.raises(TypeError, match="Tensor"):
            softmax(Value(1.0))

    @pytest.mark.unit
    def test_tensor_numerical_gradient_check(self):
        """Numerical gradient check for tensor relu."""
        eps = 1e-5
        x_data = np.array([1.0, -0.5, 2.0])

        # Analytic
        x = Tensor(x_data)
        y = relu(x)
        s = y.sum()
        s.backward()
        analytic = x.grad.copy()

        # Numerical
        numeric = np.zeros_like(x_data)
        for i in range(len(x_data)):
            x_plus = x_data.copy()
            x_plus[i] += eps
            x_minus = x_data.copy()
            x_minus[i] -= eps
            y_plus = relu(Tensor(x_plus)).sum()
            y_minus = relu(Tensor(x_minus)).sum()
            numeric[i] = (y_plus.data - y_minus.data) / (2 * eps)

        np.testing.assert_allclose(analytic, numeric, atol=1e-4)


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


class TestMCPTools:
    """MCP tool interface tests."""

    @pytest.mark.unit
    def test_autograd_compute_simple(self):
        from codomyrmex.autograd.mcp_tools import autograd_compute

        result = autograd_compute("x * x + y", {"x": 2.0, "y": 3.0})
        assert abs(result["result"] - 7.0) < 1e-9  # 4 + 3
        assert abs(result["gradients"]["x"] - 4.0) < 1e-9  # 2*x = 4
        assert abs(result["gradients"]["y"] - 1.0) < 1e-9  # dy/dy = 1

    @pytest.mark.unit
    def test_autograd_compute_activations(self):
        """Test that activations are available in autograd_compute."""
        from codomyrmex.autograd.mcp_tools import autograd_compute

        # We expect this might fail initially if activations aren't in namespace
        result = autograd_compute("relu(x) + tanh(y)", {"x": -1.0, "y": 0.0})
        assert result["result"] == 0.0  # relu(-1) + tanh(0) = 0 + 0
        assert result["gradients"]["x"] == 0.0
        assert result["gradients"]["y"] == 1.0

    @pytest.mark.unit
    def test_autograd_compute_power(self):
        from codomyrmex.autograd.mcp_tools import autograd_compute

        result = autograd_compute("x ** 3", {"x": 2.0})
        assert abs(result["result"] - 8.0) < 1e-9
        assert abs(result["gradients"]["x"] - 12.0) < 1e-9  # 3*x^2 = 12

    @pytest.mark.unit
    def test_autograd_compute_invalid_expression(self):
        from codomyrmex.autograd.mcp_tools import autograd_compute

        with pytest.raises(ValueError, match="syntax"):
            autograd_compute("x +* y", {"x": 1.0, "y": 2.0})

    @pytest.mark.unit
    def test_autograd_compute_invalid_variable(self):
        from codomyrmex.autograd.mcp_tools import autograd_compute

        with pytest.raises(ValueError, match="Invalid variable"):
            autograd_compute("x + y", {"123bad": 1.0})

    @pytest.mark.unit
    def test_gradient_check_tanh_passes(self):
        from codomyrmex.autograd.mcp_tools import autograd_gradient_check

        result = autograd_gradient_check("tanh", [0.5, 1.0, -0.5])
        assert result["passed"] is True
        assert result["max_error"] < 1e-4

    @pytest.mark.unit
    def test_gradient_check_relu_passes(self):
        from codomyrmex.autograd.mcp_tools import autograd_gradient_check

        result = autograd_gradient_check("relu", [1.0, 2.0, -1.0])
        assert result["passed"] is True

    @pytest.mark.unit
    def test_gradient_check_sigmoid_passes(self):
        from codomyrmex.autograd.mcp_tools import autograd_gradient_check

        result = autograd_gradient_check("sigmoid", [0.0, 1.0, -1.0])
        assert result["passed"] is True
        assert result["max_error"] < 1e-4

    @pytest.mark.unit
    def test_gradient_check_square_passes(self):
        from codomyrmex.autograd.mcp_tools import autograd_gradient_check

        result = autograd_gradient_check("square", [2.0, -3.0, 0.0])
        assert result["passed"] is True

    @pytest.mark.unit
    def test_gradient_check_unknown_function(self):
        from codomyrmex.autograd.mcp_tools import autograd_gradient_check

        with pytest.raises(ValueError, match="Unknown function"):
            autograd_gradient_check("nonexistent", [1.0])

    @pytest.mark.unit
    def test_mcp_tool_metadata(self):
        from codomyrmex.autograd.mcp_tools import (
            autograd_compute,
            autograd_gradient_check,
        )

        assert hasattr(autograd_compute, "_mcp_tool_meta")
        assert autograd_compute._mcp_tool_meta["category"] == "autograd"
        assert hasattr(autograd_gradient_check, "_mcp_tool_meta")
        assert autograd_gradient_check._mcp_tool_meta["category"] == "autograd"
