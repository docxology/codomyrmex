# PEFT Module

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `peft` module implements Parameter-Efficient Fine-Tuning adapters as pure NumPy implementations. It provides three PEFT methods from the literature: LoRA (Hu et al. 2021), Prefix Tuning (Li & Liang 2021), and IA3 (Liu et al. 2022). Each adapter type inherits from a common `PEFTAdapter` abstract base class, enabling uniform composition and comparison. No PyTorch dependency.

## Architecture

The module uses an adapter pattern with a shared abstract base:

- **`PEFTAdapter`** (ABC) -- defines `adapt()` and `trainable_params` interface
- **`LoRAAdapter`** -- low-rank matrices (B=0 init for identity start)
- **`PrefixTuningAdapter`** -- learned virtual tokens prepended to attention K/V
- **`IA3Adapter`** -- per-layer rescaling vectors for keys, values, and FFN activations
- **`PEFTConfig`** -- unified configuration dataclass for all methods

## Key Exports

| Export | Module | Description |
|--------|--------|-------------|
| `PEFTAdapter` | `adapters.py` | Abstract base class with `adapt()` and `trainable_params` |
| `LoRAAdapter` | `adapters.py` | LoRA: low-rank weight adaptation (rank, alpha configurable) |
| `PrefixTuningAdapter` | `adapters.py` | Prefix Tuning: learned virtual tokens for attention |
| `IA3Adapter` | `adapters.py` | IA3: per-layer rescaling vectors (l_k, l_v, l_ff) |
| `PEFTConfig` | `adapters.py` | Configuration dataclass (method, rank, alpha, num_virtual_tokens) |

## Quick Start

```python
import numpy as np
from codomyrmex.peft import LoRAAdapter, PrefixTuningAdapter, IA3Adapter

# LoRA adapter for a 512-dim layer, rank 4
lora = LoRAAdapter(d_in=512, d_out=512, rank=4, alpha=8.0)
x = np.random.randn(2, 512)
base_output = np.random.randn(2, 512)
adapted = lora.adapt(x, base_output=base_output)
print(f"LoRA trainable params: {lora.trainable_params}")  # 4096

# Prefix Tuning: 10 virtual tokens
prefix = PrefixTuningAdapter(d_model=512, n_prefix=10, n_layers=2)
seq = np.random.randn(2, 20, 512)
extended = prefix.adapt(seq, layer_idx=0)  # (2, 30, 512)

# IA3: per-layer rescaling (very parameter-efficient)
ia3 = IA3Adapter(d_model=512)
keys = np.random.randn(2, 20, 512)
scaled_keys = ia3.adapt(keys, mode="keys")
print(f"IA3 trainable params: {ia3.trainable_params}")  # ~3072
```

## Parameter Efficiency Comparison

| Method | Trainable Params (d=512, r=4) | Mechanism |
|--------|-------------------------------|-----------|
| LoRA | 4,096 | Low-rank weight delta |
| Prefix Tuning (10 tokens, 2 layers) | 20,480 | Virtual attention tokens |
| IA3 | 3,072 | Activation rescaling vectors |

## MCP Tools

This module exposes MCP tools via `mcp_tools.py` and is auto-discovered by the PAI MCP bridge.

## PAI Integration

| Phase | Usage |
|-------|-------|
| BUILD | Apply PEFT adapters to reduce fine-tuning compute |
| VERIFY | Compare adapter parameter counts and adaptation quality |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/peft/ -v
```

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public exports: PEFTAdapter, LoRAAdapter, PrefixTuningAdapter, IA3Adapter, PEFTConfig |
| `adapters.py` | All adapter implementations with shared ABC |
| `mcp_tools.py` | MCP tool definitions for PAI bridge |

## Related Modules

- [lora](../lora/) -- Standalone LoRA implementation with merge/unmerge support
- [model_merger](../model_merger/) -- Merge PEFT-adapted models
- [neural](../neural/) -- Transformer layers that PEFT adapts

## Navigation

- **AGENTS**: [AGENTS.md](AGENTS.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Source**: [`src/codomyrmex/peft/`](../../../src/codomyrmex/peft/)
- **Parent**: [Module Documentation](../README.md)
- **Root**: [docs/](../../README.md)
