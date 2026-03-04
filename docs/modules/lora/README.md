# LoRA Module

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `lora` module implements Low-Rank Adaptation (LoRA) from Hu et al. (2021) for parameter-efficient fine-tuning of large language models. A pretrained weight matrix W_0 is reparameterized as W = W_0 + B @ A * (alpha / r), where A and B are low-rank matrices with rank r much smaller than the original dimensions. During training, only A and B are updated while W_0 remains frozen. Pure Python and NumPy -- no PyTorch dependency.

## Architecture

The module centers on `LoRALayer`, which wraps a frozen base weight with trainable low-rank matrices:

- **B initialized to zero** -- ensures no modification at initialization (identity start)
- **A initialized with Kaiming uniform** -- standard He initialization
- **Merge/Unmerge support** -- merge LoRA into base weight for inference, unmerge for continued training

## Key Exports

| Export | Module | Description |
|--------|--------|-------------|
| `LoRALayer` | `lora.py` | Core LoRA adaptation layer with forward, merge, unmerge |
| `LoRAConfig` | `lora.py` | Configuration dataclass (rank, alpha, dropout, target_modules) |
| `apply_lora` | `lora.py` | Convenience function to wrap a weight matrix with LoRA |
| `merge_lora` | `lora.py` | Merge LoRA weights into base and return merged matrix |

## Quick Start

```python
import numpy as np
from codomyrmex.lora import LoRALayer, LoRAConfig, apply_lora, merge_lora

# Create a pretrained weight matrix (768 x 768)
W_pretrained = np.random.randn(768, 768) * 0.01

# Apply LoRA with rank 4, alpha 8
lora_layer = apply_lora(W_pretrained, rank=4, alpha=8.0)

# Forward pass: x @ (W_0 + B @ A * scaling)^T
x = np.random.randn(2, 768)
output = lora_layer(x)

# Merge for inference (no LoRA overhead)
merged_weight = merge_lora(lora_layer)
```

## LoRA Mathematics

The scaling factor `alpha / rank` controls the magnitude of the LoRA update:

- Higher alpha = larger LoRA contribution
- Higher rank = more expressive but more parameters
- Typical: rank=4-16, alpha=2*rank

The `effective_rank` property computes the actual matrix rank of the delta B @ A.

## MCP Tools

This module exposes MCP tools via `mcp_tools.py` and is auto-discovered by the PAI MCP bridge.

## PAI Integration

| Phase | Usage |
|-------|-------|
| BUILD | Apply LoRA adapters to model weights for fine-tuning |
| EXECUTE | Merge LoRA for efficient inference |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/lora/ -v
```

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public exports: LoRALayer, LoRAConfig, apply_lora, merge_lora |
| `lora.py` | Full LoRA implementation with merge/unmerge support |
| `mcp_tools.py` | MCP tool definitions for PAI bridge |

## Related Modules

- [peft](../peft/) -- Higher-level PEFT framework that includes LoRA as one adapter type
- [model_merger](../model_merger/) -- Merge LoRA-adapted models via SLERP or linear interpolation
- [neural](../neural/) -- Transformer layers that LoRA adapts

## Navigation

- **AGENTS**: [AGENTS.md](AGENTS.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Source**: [`src/codomyrmex/lora/`](../../../src/codomyrmex/lora/)
- **Parent**: [Module Documentation](../README.md)
- **Root**: [docs/](../../README.md)
