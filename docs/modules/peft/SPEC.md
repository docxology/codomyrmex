# Parameter-Efficient Fine-Tuning (PEFT) Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides multiple parameter-efficient fine-tuning adapters: LoRA (Low-Rank Adaptation), Prefix Tuning, and IA3 (Infused Adapter by Inhibiting and Amplifying Inner Activations). Enables fine-tuning with dramatically fewer trainable parameters.

## Functional Requirements

1. LoRAAdapter: low-rank decomposition with configurable rank and alpha scaling
2. PrefixTuningAdapter: learned prefix key-value pairs prepended to attention
3. IA3Adapter: element-wise rescaling of keys, values, and feedforward activations
4. Unified PEFTConfig for adapter hyperparameter management


## Interface

```python
from codomyrmex.peft import LoRAAdapter, PrefixTuningAdapter, IA3Adapter, PEFTConfig

lora = LoRAAdapter(d_in=768, d_out=768, rank=4, alpha=8.0)
prefix = PrefixTuningAdapter(d_model=768)
ia3 = IA3Adapter(d_model=768)
print(lora.trainable_params, prefix.trainable_params, ia3.trainable_params)
```

## Exports

PEFTAdapter, LoRAAdapter, PrefixTuningAdapter, IA3Adapter, PEFTConfig

## Navigation

- [Source README](../../src/codomyrmex/peft/README.md) | [AGENTS.md](AGENTS.md)
