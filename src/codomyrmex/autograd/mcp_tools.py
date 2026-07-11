"""
MCP tools for the autograd module.

Exposes automatic differentiation capabilities through the Model Context
Protocol so that AI agents can evaluate expressions and verify gradients.
"""

from __future__ import annotations

import ast
import operator
from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .engine import Value
from .ops import relu, sigmoid, tanh

# ---------------------------------------------------------------------------
# Safe expression evaluator
# ---------------------------------------------------------------------------

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node: ast.AST, namespace: dict[str, Any]) -> Any:
    """Recursively evaluate an AST node safely."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body, namespace)
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float)):
            raise ValueError(f"Unsupported constant type: {type(node.value)}")
        return node.value
    if isinstance(node, ast.Name):
        if node.id in namespace:
            return namespace[node.id]
        raise ValueError(f"Unknown variable or function: {node.id}")
    if isinstance(node, ast.BinOp):
        left = _safe_eval(node.left, namespace)
        right = _safe_eval(node.right, namespace)
        op_type = type(node.op)
        if op_type in _ALLOWED_OPS:
            return _ALLOWED_OPS[op_type](left, right)
        raise ValueError(f"Unsupported operation: {op_type.__name__}")
    if isinstance(node, ast.UnaryOp):
        operand = _safe_eval(node.operand, namespace)
        op_type = type(node.op)
        if op_type in _ALLOWED_OPS:
            return _ALLOWED_OPS[op_type](operand)
        raise ValueError(f"Unsupported unary operation: {op_type.__name__}")
    if isinstance(node, ast.Call):
        if node.keywords:
            raise ValueError("Keyword arguments are not supported in function calls")
        if isinstance(node.func, ast.Name):
            if node.func.id not in namespace:
                raise ValueError(f"Unknown function: {node.func.id}")
            func = namespace[node.func.id]
            args = [_safe_eval(arg, namespace) for arg in node.args]
            return func(*args)
        raise ValueError("Unsupported function call syntax")
    raise ValueError(f"Unsupported syntax: {type(node).__name__}")


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp_tool(category="autograd")
def autograd_compute(expression: str, variables: dict) -> dict:
    """Evaluate a simple expression and compute its gradient.

    Args:
        expression: Simple math expression like "x*x + y" using +,-,*,** ops.
            Available functions: relu, tanh, sigmoid.
        variables: dict of variable names to float values, e.g. {"x": 2.0, "y": 3.0}

    Returns:
        dict with keys: result (float), gradients (dict of var->grad)
    """
    # Build Value objects for each variable
    var_values: dict[str, Value] = {}
    namespace: dict[str, Any] = {
        "__builtins__": {},
        "relu": relu,
        "tanh": tanh,
        "sigmoid": sigmoid,
    }

    for name, val in variables.items():
        if not name.isidentifier():
            raise ValueError(f"Invalid variable name: {name!r}")
        v = Value(float(val), label=name)
        var_values[name] = v
        namespace[name] = v

    # Parse and safely evaluate
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree, namespace)
    except SyntaxError as exc:
        raise ValueError(f"Invalid expression syntax: {exc}") from exc
    except ValueError as exc:
        raise ValueError(f"Expression evaluation error: {exc}") from exc

    if not isinstance(result, Value):
        result = Value(float(result))

    # Run backward pass
    result.backward()

    # Collect gradients
    gradients = {name: v.grad for name, v in var_values.items()}

    return {
        "result": result.data,
        "gradients": gradients,
    }


@mcp_tool(category="autograd")
def autograd_gradient_check(func_name: str, inputs: list) -> dict:
    """Numerically verify that analytic gradients match finite differences.

    Args:
        func_name: One of "relu", "tanh", "sigmoid", "square", "sum"
        inputs: list of input values

    Returns:
        dict with: max_error (float), passed (bool), analytic_grads, numeric_grads
    """
    eps = 1e-5

    func_map = {
        "relu": relu,
        "tanh": tanh,
        "sigmoid": sigmoid,
        "square": lambda v: v * v,
        "sum": lambda v: v,  # identity for scalar
    }

    if func_name not in func_map:
        raise ValueError(
            f"Unknown function: {func_name!r}. Supported: {sorted(func_map.keys())}"
        )

    fn = func_map[func_name]
    analytic_grads = []
    numeric_grads = []
    errors = []

    for x_val in inputs:
        x_val = float(x_val)

        # Analytic gradient
        x = Value(x_val)
        y = fn(x)
        y.backward()
        a_grad = x.grad

        # Numerical gradient (central differences)
        x_plus = Value(x_val + eps)
        y_plus = fn(x_plus)
        x_minus = Value(x_val - eps)
        y_minus = fn(x_minus)
        n_grad = (y_plus.data - y_minus.data) / (2 * eps)

        analytic_grads.append(a_grad)
        numeric_grads.append(n_grad)
        errors.append(abs(a_grad - n_grad))

    max_error = max(errors) if errors else 0.0

    return {
        "max_error": max_error,
        "passed": max_error < 1e-4,
        "analytic_grads": analytic_grads,
        "numeric_grads": numeric_grads,
    }
