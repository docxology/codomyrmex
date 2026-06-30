# Distributed Training - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `distributed_training` module provides FSDP (Fully Sharded Data Parallel) and tensor parallelism simulation. Enables prototyping distributed training strategies without requiring actual multi-GPU hardware.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `FSDPShard` | Represents a model shard in FSDP across a simulated device |
| `AllReduce` | Simulates all-reduce gradient synchronisation across shards |

### 2.2 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `simulate_fsdp_step` | `(model_params, num_shards, ...) -> dict` | Run one simulated FSDP training step across shards |

## 3. Usage Example

```python
from codomyrmex.distributed_training import simulate_fsdp_step
import numpy as np

params = {"weight": np.random.randn(128, 64)}
result = simulate_fsdp_step(params, num_shards=4)
print(result["step_time_ms"], result["communication_overhead"])
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
