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
    "**": operator.pow,
}

_AST_OPS = {
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Pow: "**",
}


def _get_exponent_value(node: ast.AST) -> float:
    """Helper to extract a constant float/int exponent."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        if isinstance(node.operand, ast.Constant) and isinstance(
            node.operand.value, (int, float)
        ):
            return -float(node.operand.value)
    raise ValueError("Exponent must be a constant float or integer")


def _safe_eval(node: ast.AST, variables: dict[str, Value]) -> Value:
    """Safely evaluate an AST node containing a mathematical expression."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body, variables)
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _AST_OPS:
            raise ValueError(f"Unsupported operation: {op_type.__name__}")

        op_str = _AST_OPS[op_type]
        op_func = _ALLOWED_OPS[op_str]

        left = _safe_eval(node.left, variables)

        # Value**Value is not supported in engine.py, exponent must be a float/int
        if op_type == ast.Pow:
            right = _get_exponent_value(node.right)
        else:
            right = _safe_eval(node.right, variables)

        return op_func(left, right)
    elif isinstance(node, ast.Name):
        if node.id in variables:
            return variables[node.id]
        raise ValueError(f"Undefined variable: {node.id}")
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return Value(float(node.value))
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.USub):
            return -_safe_eval(node.operand, variables)
        elif isinstance(node.op, ast.UAdd):
            return _safe_eval(node.operand, variables)
        raise ValueError(f"Unsupported unary operation: {type(node.op).__name__}")
    else:
        raise ValueError(f"Unsupported AST node: {type(node).__name__}")


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp_tool(category="autograd")
def autograd_compute(expression: str, variables: dict) -> dict:
    """Evaluate a simple expression and compute its gradient.

    Args:
        expression: Simple math expression like "x*x + y" using +,-,*,** ops
        variables: Dict of variable names to float values, e.g. {"x": 2.0, "y": 3.0}

    Returns:
        dict with keys: result (float), gradients (dict of var->grad)
    """
    # Build Value objects for each variable
    var_values: dict[str, Value] = {}

    for name, val in variables.items():
        if not name.isidentifier():
            raise ValueError(f"Invalid variable name: {name!r}")
        v = Value(float(val), label=name)
        var_values[name] = v

    # Parse and safely evaluate
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid expression syntax: {exc}") from exc

    result = _safe_eval(tree, var_values)

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
        inputs: List of input values

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
