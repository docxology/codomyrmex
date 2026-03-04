# Autograd — MCP Tool Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `autograd` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

The autograd module provides automatic differentiation capabilities, allowing
AI agents to evaluate mathematical expressions and verify gradient computations.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `autograd` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `autograd_compute`

**Description**: Evaluate a simple expression and compute its gradient via reverse-mode automatic differentiation.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `expression` | `str` | Yes | -- | Simple math expression like `"x*x + y"` using `+`, `-`, `*`, `**` operators |
| `variables` | `dict` | Yes | -- | Dict of variable names to float values, e.g. `{"x": 2.0, "y": 3.0}` |

**Returns**: `dict` — Dictionary with `result` (float, the expression value) and `gradients` (dict mapping variable names to their gradient values).

**Example**:
```python
from codomyrmex.autograd.mcp_tools import autograd_compute

result = autograd_compute(expression="x*x + y", variables={"x": 3.0, "y": 1.0})
# {"result": 10.0, "gradients": {"x": 6.0, "y": 1.0}}
```

**Notes**: Uses a restricted eval with no builtins. Only supports `+`, `-`, `*`, `**` operators and variable names that are valid Python identifiers.

---

### `autograd_gradient_check`

**Description**: Numerically verify that analytic gradients match finite differences.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `func_name` | `str` | Yes | -- | One of `"relu"`, `"tanh"`, `"sigmoid"`, `"square"`, `"sum"` |
| `inputs` | `list` | Yes | -- | List of input values to check gradients at |

**Returns**: `dict` — Dictionary with `max_error` (float), `passed` (bool, true if max_error < 1e-4), `analytic_grads` (list), and `numeric_grads` (list).

**Example**:
```python
from codomyrmex.autograd.mcp_tools import autograd_gradient_check

result = autograd_gradient_check(func_name="sigmoid", inputs=[0.0, 1.0, -1.0])
# {"max_error": 1.2e-10, "passed": true, ...}
```

**Notes**: Uses central finite differences with epsilon=1e-5. Supported functions: `relu`, `tanh`, `sigmoid`, `square`, `sum`.

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe — no trust check required
- **PAI Phases**: VERIFY (gradient correctness validation), BUILD (expression evaluation)
- **Dependencies**: `autograd.engine.Value`, `autograd.ops` (relu, sigmoid, tanh)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
