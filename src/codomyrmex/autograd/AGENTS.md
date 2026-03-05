# Autograd -- Agent Integration Guide

## Module Purpose

Provides from-scratch automatic differentiation for AI agents that need gradient computation, numerical optimization, or educational demonstrations of backpropagation.

## MCP Tools

| Tool | Description | Inputs | Output |
|------|-------------|--------|--------|
| `autograd_compute` | Evaluate expression and compute gradients | `expression: str`, `variables: dict` | `{result, gradients}` |
| `autograd_gradient_check` | Verify analytic vs numerical gradients | `func_name: str`, `inputs: list[float]` | `{max_error, passed, analytic_grads, numeric_grads}` |

## Agent Use Cases

### Gradient Computation
An agent can use `autograd_compute` to find derivatives of mathematical expressions without symbolic math libraries.

### Gradient Verification
Use `autograd_gradient_check` to verify that a function's analytic gradient implementation is correct by comparing against finite differences.

### Educational / Explanation
Agents can demonstrate how backpropagation works by building Value computation graphs and showing step-by-step gradient flow.

## Example Agent Workflow

```
1. Agent receives: "What is the derivative of x^3 + 2x at x=3?"
2. Agent calls: autograd_compute("x**3 + 2*x", {"x": 3.0})
3. Response: {"result": 33.0, "gradients": {"x": 29.0}}
4. Agent explains: f'(x) = 3x^2 + 2 = 27 + 2 = 29
```

## Supported Functions for Gradient Check

- `relu` -- max(0, x)
- `tanh` -- hyperbolic tangent
- `sigmoid` -- logistic function
- `square` -- x^2
- `sum` -- identity (for scalar inputs)

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full — design, implement, train, benchmark | All available | TRUSTED |
| **Architect** | Read + Architecture review | Read-only | SAFE |
| **QATester** | Validation + output verification | Read + Inspect | SAFE |
| **Researcher** | Read-only — study algorithms and outputs | None | OBSERVED |
