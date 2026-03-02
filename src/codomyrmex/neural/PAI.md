# Neural -- PAI Integration

## Phase Mapping

| PAI Phase | Tool | Usage |
|-----------|------|-------|
| OBSERVE | `attention_forward` | Inspect attention weight distributions for a given configuration |
| THINK | `transformer_encode` | Explore encoder hyperparameters (d_model, n_heads, n_layers) |
| BUILD | Python API (`MultiHeadAttention`, `TransformerEncoder`, etc.) | Build custom neural architectures |
| VERIFY | `transformer_encode`, `attention_forward` | Validate output shapes and attention normalization |
| LEARN | `attention_forward` | Analyze attention patterns for knowledge extraction |

## MCP Tools

| Tool Name | Category | Description |
|-----------|----------|-------------|
| `transformer_encode` | neural | Run forward pass through random Transformer encoder |
| `attention_forward` | neural | Run multi-head attention on random inputs |

## Agent Providers

This module does not provide agent types. It provides neural network primitives that agents consume.

## Dependencies

- Foundation: `model_context_protocol` (for `@mcp_tool` decorator)
- External: `numpy`
