"""
MCP tools for the autograd module.

Exposes automatic differentiation capabilities through the Model Context
Protocol so that AI agents can evaluate expressions and verify gradients.
"""

from __future__ import annotations

import ast
import operator

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .engine import Value
from .ops import relu, sigmoid, tanh

# ---------------------------------------------------------------------------
# Safe expression evaluator
# ---------------------------------------------------------------------------

_MATH_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _safe_eval_node(node: ast.AST, variables: dict[str, Value]) -> Value:
    """Evaluate an AST node using Value objects."""
    if isinstance(node, ast.Expression):
        return _safe_eval_node(node.body, variables)
    elif isinstance(node, ast.BinOp):
        left = _safe_eval_node(node.left, variables)
        right = _safe_eval_node(node.right, variables)
        if type(node.op) not in _MATH_OPS:
            raise ValueError(f"Unsupported operator: {type(node.op)}")

        if isinstance(node.op, ast.Pow):
            # Value.__pow__ only supports float/int exponent
            exponent = right.data if isinstance(right, Value) else right
            return _MATH_OPS[type(node.op)](left, exponent)

        return _MATH_OPS[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp):
        operand = _safe_eval_node(node.operand, variables)
        if type(node.op) not in _MATH_OPS:
            raise ValueError(f"Unsupported unary operator: {type(node.op)}")
        return _MATH_OPS[type(node.op)](operand)
    elif isinstance(node, ast.Name):
        if node.id not in variables:
            raise ValueError(f"Unknown variable: {node.id}")
        return variables[node.id]
    elif isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float)):
            raise ValueError(f"Unsupported constant type: {type(node.value)}")
        # If it's used in a power operation (which gets caught here recursively),
        # we want to allow float directly. But since we evaluate bottom-up,
        # let's return Value, and in pow we'll extract it or handle it.
        # Actually, Value.__pow__ takes a float, so if `right` is a Value,
        # we need to extract its data in the `ast.Pow` handling.
        return Value(float(node.value))
    else:
        raise ValueError(f"Unsupported expression construct: {type(node)}")


def _safe_eval_expression(expression: str, variables: dict[str, float]) -> Value:
    """Evaluate a simple math expression using Value objects.

    Supports: variable names, float literals, +, -, *, **, parentheses,
    unary minus. Uses AST-based evaluation instead of eval() to prevent
    code injection.
    """
    # Build Value-wrapped variables
    var_values: dict[str, Value] = {}
    for name, val in variables.items():
        if not name.isidentifier():
            raise ValueError(f"Invalid variable name: {name!r}")
        var_values[name] = Value(float(val), label=name)

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid expression syntax: {exc}") from exc

    return _safe_eval_node(tree, var_values)


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
        var_values[name] = Value(float(val), label=name)

    # Parse and evaluate expression safely using AST
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid expression syntax: {exc}") from exc

    result = _safe_eval_node(tree, var_values)

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
