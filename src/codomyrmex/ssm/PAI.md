# SSM Module -- PAI Integration

## Phase Mapping

| PAI Phase | Tool | Usage |
|-----------|------|-------|
| BUILD | `ssm_forward` | Generate Mamba SSM outputs for sequence modeling tasks |
| BUILD | `flash_attention_forward` | Run Flash Attention with correctness verification |
| VERIFY | `flash_attention_forward` | Verify flash vs standard attention numerical accuracy |
| OBSERVE | `ssm_forward` | Inspect output shapes and model configuration |

## Capabilities

### Sequence Modeling (BUILD)
- `ssm_forward(sequence_length=128, d_model=64, d_state=16, n_layers=4)` -- run stacked Mamba
- `flash_attention_forward(seq_len=64, d_model=32, block_size=8)` -- memory-efficient attention

### Correctness Verification (VERIFY)
- `flash_attention_forward` returns `max_error_vs_standard` and `passed` boolean
- Error should be < 1e-4 for float32 inputs

## Integration Notes

- Both tools are auto-discovered via `@mcp_tool` decorator in `ssm/mcp_tools.py`
- Pure NumPy: no GPU dependencies, runs anywhere
- Flash Attention references `codomyrmex.neural.attention.scaled_dot_product_attention` for verification
- Mamba SSM is fully self-contained within the `ssm` package
