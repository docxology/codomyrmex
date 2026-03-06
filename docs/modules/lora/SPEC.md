# LoRA (Low-Rank Adaptation) Specification

**Version**: v1.1.6 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements Low-Rank Adaptation (LoRA) for parameter-efficient fine-tuning. Decomposes weight update matrices into low-rank factors, enabling fine-tuning with a fraction of the original parameters.

## Functional Requirements

1. Low-rank decomposition of weight updates into A (d x r) and B (r x k) matrices
2. Configurable rank and alpha scaling via LoRAConfig
3. Merge LoRA weights back into the base model for inference


## Interface

```python
from codomyrmex.lora import LoRALayer, LoRAConfig, apply_lora, merge_lora

layer = apply_lora(weight_matrix, rank=4, alpha=8.0)
merged = merge_lora(base_weights, layer)
```

## Exports

LoRALayer, LoRAConfig, apply_lora, merge_lora

## Navigation

- [Source README](../../src/codomyrmex/lora/README.md) | [AGENTS.md](AGENTS.md)
