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
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "**": operator.pow,
}


def _safe_eval(expr: str, namespace: dict[str, Any]) -> Any:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid expression syntax: {exc}") from exc

    def _eval(node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in namespace:
                return namespace[node.id]
            raise NameError(f"name {node.id!r} is not defined")
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            if isinstance(node.op, ast.Add):
                return _ALLOWED_OPS["+"](left, right)
            if isinstance(node.op, ast.Sub):
                return _ALLOWED_OPS["-"](left, right)
            if isinstance(node.op, ast.Mult):
                return _ALLOWED_OPS["*"](left, right)
            if isinstance(node.op, ast.Div):
                return _ALLOWED_OPS["/"](left, right)
            if isinstance(node.op, ast.Pow):
                return _ALLOWED_OPS["**"](left, right)
            raise ValueError(
                f"Unsupported binary operator: {type(node.op).__name__}"
            )
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            if isinstance(node.op, ast.UAdd):
                return operator.pos(operand)
            if isinstance(node.op, ast.USub):
                return operator.neg(operand)
            raise ValueError(
                f"Unsupported unary operator: {type(node.op).__name__}"
            )
        if isinstance(node, ast.Call):
            func = _eval(node.func)
            if not callable(func):
                raise TypeError(f"'{type(func).__name__}' object is not callable")
            args = [_eval(arg) for arg in node.args]
            if node.keywords:
                raise ValueError("Keyword arguments are not supported")
            return func(*args)
        raise ValueError(f"Unsupported expression node: {type(node).__name__}")

    return _eval(tree.body)


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

    # Safely evaluate using AST parsing
    result = _safe_eval(expression, namespace)

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
