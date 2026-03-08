# Autograd Module

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `autograd` module provides a from-scratch automatic differentiation engine inspired by Andrej Karpathy's Micrograd. It implements reverse-mode autodiff for both scalar values and NumPy-backed tensors, building computation graphs (DAGs) that are walked in reverse topological order to accumulate gradients via the chain rule. Pure Python and NumPy -- no PyTorch dependency.

## Architecture

The module is split into two files:

- **`engine.py`** -- Core autodiff primitives (`Value` and `Tensor`)
- **`ops.py`** -- Activation functions that work with both `Value` and `Tensor` types

Computation graphs are built implicitly during forward operations. Each node stores its `_backward` closure, and calling `backward()` on the output traverses the graph in reverse to compute gradients.

## Key Exports

| Export | Module | Description |
|--------|--------|-------------|
| `Value` | `engine.py` | Scalar autograd node with full arithmetic operator support |
| `Tensor` | `engine.py` | NumPy-backed tensor with gradient accumulation |
| `relu` | `ops.py` | ReLU activation for Value or Tensor |
| `tanh` | `ops.py` | Hyperbolic tangent activation |
| `sigmoid` | `ops.py` | Sigmoid activation: 1/(1+exp(-x)) |
| `softmax` | `ops.py` | Numerically stable softmax (Tensor only) |

## Quick Start

```python
from codomyrmex.autograd import Value, relu

# Build a computation graph
x = Value(2.0, label="x")
y = Value(3.0, label="y")
z = relu(x * y + Value(1.0))

# Backward pass computes gradients
z.backward()
print(f"dz/dx = {x.grad}")  # 3.0 (y's value, gated by ReLU)
print(f"dz/dy = {y.grad}")  # 2.0 (x's value, gated by ReLU)
```

## Value Operations

`Value` supports full arithmetic (`+`, `-`, `*`, `/`, `**`) including reverse operators (`radd`, `rmul`, etc.) and special math operations:

- `exp()` -- e^x with correct backward
- `tanh()` -- hyperbolic tangent
- `relu()` -- max(0, x)
- `sigmoid()` -- logistic function
- `backward()` -- reverse-mode autodiff via topological sort

## MCP Tools

This module exposes MCP tools via `mcp_tools.py` and is auto-discovered by the PAI MCP bridge.

## PAI Integration

| Phase | Usage |
|-------|-------|
| BUILD | Gradient computation for custom training loops |
| VERIFY | Gradient checking and numerical validation |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/autograd/ -v
```

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public exports: Value, Tensor, relu, tanh, sigmoid, softmax |
| `engine.py` | Value (scalar) and Tensor (ndarray) autograd implementations |
| `ops.py` | Activation functions with dual Value/Tensor support |
| `mcp_tools.py` | MCP tool definitions for PAI bridge |

## Related Modules

- [neural](../neural/) -- Uses autograd primitives for transformer layers
- [softmax_opt](../softmax_opt/) -- Optimized softmax implementations
- [distillation](../distillation/) -- Training pipelines that benefit from autograd

## Navigation

- **AGENTS**: [AGENTS.md](AGENTS.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Source**: [`src/codomyrmex/autograd/`](../../../src/codomyrmex/autograd/)
- **Parent**: [Module Documentation](../README.md)
- **Root**: [docs/](../../README.md)
