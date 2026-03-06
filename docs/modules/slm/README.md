# SLM (Small Language Models) Module

**Version**: v1.1.6 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `slm` module provides a complete GPT-2 style decoder-only transformer built from scratch with NumPy. It includes token embedding with sinusoidal positional encoding, N pre-LN transformer decoder blocks with causal self-attention, a language model head, and greedy autoregressive generation. Designed for on-device and edge inference experimentation. Pure Python and NumPy -- no PyTorch dependency.

## Architecture

The module is contained in `model.py` with three components:

- **`SLMConfig`** -- configuration dataclass (vocab_size, d_model, n_heads, n_layers, d_ff, max_seq_len)
- **`SLM`** -- the full GPT-2 architecture with `forward()` and `generate()`
- **`causal_mask()`** -- lower-triangular boolean mask for autoregressive attention

The SLM reuses components from the `neural` module (MultiHeadAttention, FeedForward, LayerNorm) when available, falling back to inline implementations if `neural` is not importable.

## Key Exports

| Export | Module | Description |
|--------|--------|-------------|
| `SLM` | `model.py` | GPT-2 style decoder-only transformer |
| `SLMConfig` | `model.py` | Model configuration (vocab_size, d_model, n_heads, n_layers, etc.) |
| `causal_mask` | `model.py` | Lower-triangular boolean attention mask |

## Quick Start

```python
import numpy as np
from codomyrmex.slm import SLM, SLMConfig

# Create a small model
config = SLMConfig(vocab_size=1000, d_model=64, n_heads=4, n_layers=2, d_ff=256)
model = SLM(config)

# Forward pass: (batch, seq) -> (batch, seq, vocab_size)
token_ids = np.array([[1, 42, 7, 100]])
logits = model(token_ids)
print(f"Logits shape: {logits.shape}")  # (1, 4, 1000)

# Autoregressive generation
generated = model.generate(prompt_ids=[1, 42], max_new_tokens=10)
print(f"Generated {len(generated)} tokens")
```

## Default Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `vocab_size` | 1000 | Vocabulary size |
| `d_model` | 64 | Model dimension |
| `n_heads` | 4 | Attention heads |
| `n_layers` | 2 | Transformer blocks |
| `d_ff` | 256 | Feed-forward inner dimension |
| `max_seq_len` | 128 | Maximum sequence length |
| `dropout` | 0.0 | Dropout rate |

## MCP Tools

This module exposes MCP tools via `mcp_tools.py` and is auto-discovered by the PAI MCP bridge.

## PAI Integration

| Phase | Usage |
|-------|-------|
| BUILD | Construct small transformer models for experimentation |
| EXECUTE | Run inference and autoregressive generation |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/slm/ -v
```

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public exports: SLM, SLMConfig, causal_mask |
| `model.py` | Full GPT-2 architecture with generation support |
| `mcp_tools.py` | MCP tool definitions for PAI bridge |

## Related Modules

- [neural](../neural/) -- Transformer primitives (MultiHeadAttention, LayerNorm, FeedForward) used by SLM
- [distillation](../distillation/) -- Distill larger models into SLM-sized students
- [logit_processor](../logit_processor/) -- Sampling strategies for SLM generation output
- [dpo](../dpo/) -- Align SLM via Direct Preference Optimization

## Navigation

- **AGENTS**: [AGENTS.md](AGENTS.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Source**: [`src/codomyrmex/slm/`](../../../src/codomyrmex/slm/)
- **Parent**: [Module Documentation](../README.md)
- **Root**: [docs/](../../README.md)
