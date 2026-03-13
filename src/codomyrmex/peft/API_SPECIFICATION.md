# PEFT - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `peft` module provides Parameter-Efficient Fine-Tuning adapters including LoRA, Prefix Tuning, and IA3. All adapters share a common interface for applying, training, and merging with base model weights.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `PEFTAdapter` | Abstract base class for all PEFT adapters |
| `PEFTConfig` | Configuration dataclass (adapter type, rank, target modules) |
| `LoRAAdapter` | Low-Rank Adaptation adapter |
| `PrefixTuningAdapter` | Virtual prefix token adapter for attention layers |
| `IA3Adapter` | Infused Adapter by Inhibiting and Amplifying Inner Activations |

## 3. Usage Example

```python
from codomyrmex.peft import PEFTConfig, LoRAAdapter

config = PEFTConfig(adapter_type="lora", rank=16, target_modules=["q_proj", "v_proj"])
adapter = LoRAAdapter(config)

adapted_weights = adapter.apply(base_model_weights)
# After training:
merged_weights = adapter.merge(base_model_weights)
```

## 4. Related Modules

| Module | Relationship |
|--------|-------------|
| `lora` | Dedicated LoRA implementation (lower-level) |

## 5. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
