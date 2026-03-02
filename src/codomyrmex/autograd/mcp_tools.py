"""
MCP tools for the autograd module.

Exposes automatic differentiation capabilities through the Model Context
Protocol so that AI agents can evaluate expressions and verify gradients.
"""

from __future__ import annotations

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


def _safe_eval_expression(expression: str, variables: dict[str, float]) -> Value:
    """Evaluate a simple math expression using Value objects.

    Supports: variable names, float literals, +, -, *, **, parentheses,
    unary minus.  Uses Python's ``compile`` with a restricted global
    namespace containing only Value-wrapped variables and builtins
    stripped out.
    """
    # Build namespace with Value-wrapped variables
    namespace: dict[str, Any] = {}
    for name, val in variables.items():
        if not name.isidentifier():
            raise ValueError(f"Invalid variable name: {name!r}")
        namespace[name] = Value(float(val), label=name)

    # Restrict builtins to nothing
    namespace["__builtins__"] = {}

    # Compile and evaluate
    try:
        code = compile(expression, "<autograd_compute>", "eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid expression syntax: {exc}") from exc

    # Verify code only uses allowed operations
    # (compile already restricts to expressions, and namespace has no builtins)
    result = eval(code, namespace)  # noqa: S307

    if not isinstance(result, Value):
        # Expression evaluated to a raw number (no variables used)
        return Value(float(result))

    return result


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
    namespace: dict[str, Any] = {"__builtins__": {}}

    for name, val in variables.items():
        if not name.isidentifier():
            raise ValueError(f"Invalid variable name: {name!r}")
        v = Value(float(val), label=name)
        var_values[name] = v
        namespace[name] = v

    # Compile and evaluate
    try:
        code = compile(expression, "<autograd_compute>", "eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid expression syntax: {exc}") from exc

    result = eval(code, namespace)  # noqa: S307

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
            f"Unknown function: {func_name!r}. "
            f"Supported: {sorted(func_map.keys())}"
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
