# LoRA - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `lora` module implements Low-Rank Adaptation (LoRA) for parameter-efficient fine-tuning. Adds trainable low-rank decomposition matrices to frozen model weights, reducing the number of parameters to train.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `LoRALayer` | A single LoRA adapter layer (low-rank A and B matrices) |
| `LoRAConfig` | Configuration dataclass (rank, alpha, target modules, dropout) |

### 2.2 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `apply_lora` | `(model_weights, config) -> dict` | Apply LoRA adapters to target weight matrices |
| `merge_lora` | `(model_weights, lora_weights, alpha) -> dict` | Merge LoRA adapters back into base model weights |

## 3. Usage Example

```python
from codomyrmex.lora import LoRAConfig, apply_lora, merge_lora

config = LoRAConfig(rank=8, alpha=16, target_modules=["q_proj", "v_proj"])
lora_weights = apply_lora(model_weights, config)

# After training, merge back
merged = merge_lora(model_weights, lora_weights, alpha=16)
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
