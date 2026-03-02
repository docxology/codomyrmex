# SSM Module -- Agent Integration

## Module Purpose

Provides state space model primitives (Mamba/S6) for AI agents that need sequence modeling capabilities beyond attention-based Transformers. Useful for long-sequence tasks where O(N) complexity is required.

## Available Tools

| Tool | Category | Description |
|------|----------|-------------|
| `ssm_forward` | ssm | Run forward pass through stacked Mamba blocks |
| `flash_attention_forward` | neural | Run Flash Attention with standard-attention verification |

## Agent Usage Patterns

### Sequence Modeling Agent
```
1. Call ssm_forward with desired sequence_length, d_model, d_state
2. Inspect output_shape to verify dimensions
3. Compare with transformer_encode for attention-based alternative
```

### Architecture Comparison Agent
```
1. Call ssm_forward (O(N) complexity) for long sequences
2. Call flash_attention_forward (O(N) memory, O(N^2) compute) for comparison
3. Evaluate trade-offs: SSM for speed, attention for quality on short sequences
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `d_model` | 16 | Model dimension (width) |
| `d_state` | 8 | SSM hidden state dimension |
| `n_layers` | 2 | Number of stacked Mamba blocks |
| `sequence_length` | 8 | Input sequence length |

## Constraints

- Pure NumPy implementation: suitable for prototyping and testing, not production inference
- Random weight initialization: outputs are not meaningful without training
- Sequential scan: no parallel scan optimization (would need GPU kernels)
