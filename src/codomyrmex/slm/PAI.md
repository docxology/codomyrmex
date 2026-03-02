# SLM -- PAI Integration

## Phase Mapping

| PAI Phase | Tool | Usage |
|-----------|------|-------|
| OBSERVE | `slm_forward` | Check model output shapes and logit distributions |
| THINK | `slm_forward` | Analyze logit statistics for different configurations |
| BUILD | `SLM`, `SLMConfig` (Python API) | Build transformer models |
| EXECUTE | `slm_generate` | Generate token sequences |
| VERIFY | `slm_forward` | Validate output shapes match expectations |

## MCP Tools

| Tool Name | Category | Description |
|-----------|----------|-------------|
| `slm_generate` | slm | Generate tokens from a tiny language model |
| `slm_forward` | slm | Run forward pass and return logit statistics |

## Agent Providers

This module does not provide agent types. It provides computational tools that agents consume.

## Dependencies

- Foundation: `model_context_protocol` (for `@mcp_tool` decorator)
- Core: `neural` (optional, provides attention/layers)
- External: `numpy`
