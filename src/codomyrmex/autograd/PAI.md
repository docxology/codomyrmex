# Autograd -- PAI Integration

## Phase Mapping

| PAI Phase | Tool | Usage |
|-----------|------|-------|
| OBSERVE | `autograd_gradient_check` | Verify gradient correctness of a function |
| THINK | `autograd_compute` | Compute derivatives to inform optimization decisions |
| BUILD | `Value`, `Tensor` (Python API) | Build differentiable computation graphs |
| VERIFY | `autograd_gradient_check` | Validate analytic gradients against numerical |
| LEARN | `autograd_compute` | Explore parameter sensitivities |

## MCP Tools

| Tool Name | Category | Description |
|-----------|----------|-------------|
| `autograd_compute` | autograd | Evaluate expression and return value + gradients |
| `autograd_gradient_check` | autograd | Compare analytic vs numerical gradients |

## Agent Providers

This module does not provide agent types. It provides computational tools that agents consume.

## Dependencies

- Foundation: `model_context_protocol` (for `@mcp_tool` decorator)
- External: `numpy`
