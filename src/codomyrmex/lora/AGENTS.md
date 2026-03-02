# Agent Guidelines -- LoRA

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

LoRA (Low-Rank Adaptation) provides parameter-efficient fine-tuning via low-rank weight decomposition.
A pretrained weight W_0 is adapted as W = W_0 + B @ A * (alpha / r) where only A and B are trainable.
One MCP tool (`lora_apply`) exposes the LoRA lifecycle to PAI agents.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `LoRALayer`, `LoRAConfig`, `apply_lora`, `merge_lora` |
| `lora.py` | Core LoRA implementation (LoRALayer, LoRAConfig) |
| `mcp_tools.py` | MCP tool: `lora_apply` |

## Key Classes

- **LoRAConfig** -- Configuration dataclass (rank, alpha, dropout, target_modules, scaling property)
- **LoRALayer** -- LoRA weight adaptation layer (forward, merge, unmerge, get_delta, effective_rank)

## Agent Instructions

1. **Apply LoRA** -- Use `apply_lora(weight, rank, alpha)` to wrap a weight matrix
2. **Forward** -- Call `layer(x)` or `layer.forward(x)` for the adapted output
3. **Merge** -- Use `merge_lora(layer)` for inference (eliminates LoRA overhead)
4. **Unmerge** -- Use `layer.unmerge(original_W)` to restore for continued training

## Common Patterns

```python
from codomyrmex.lora import apply_lora, merge_lora
import numpy as np

W = np.random.randn(512, 256)
layer = apply_lora(W, rank=8, alpha=16.0)

# Forward pass
x = np.random.randn(4, 256)
output = layer(x)

# Merge for deployment
W_merged = merge_lora(layer)
```

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `lora_apply` | Apply LoRA to a weight matrix and report parameter efficiency | SAFE |

## Operating Contracts

- `LoRALayer` creates a copy of the weight matrix -- the original is not modified
- B is initialized to zero so initial delta = 0 (no change from pretrained)
- `merge()` is idempotent -- calling it twice does not double-add the delta
- `unmerge()` requires the original weight to be passed explicitly

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full CRUD | `lora_apply` | SAFE |
| **Architect** | Parameter analysis | `lora_apply` -- efficiency estimation | SAFE |
| **QATester** | Verification | `lora_apply` -- validate parameter counts | SAFE |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
