# Distributed Training -- FSDP Simulation

A pure Python + NumPy simulation of distributed training primitives including Fully Sharded Data Parallel (FSDP) and Distributed Data Parallel (DDP) collective operations.

## Overview

This module simulates distributed training mechanics without requiring actual multi-GPU hardware or NCCL:

- **FSDP**: Shards parameters across devices; uses AllGather and ReduceScatter
- **DDP**: AllReduce for gradient synchronization (sum or mean)
- **SGD Step**: Simulates one complete optimizer step with gradient averaging

## Quick Start

```python
import numpy as np
from codomyrmex.distributed_training import FSDPShard, AllReduce, simulate_fsdp_step
from codomyrmex.distributed_training.fsdp import all_gather, reduce_scatter

# Simulate FSDP with 4 GPUs
params = np.random.randn(1024)
gradients = [np.random.randn(1024) for _ in range(4)]

new_params, shards = simulate_fsdp_step(
    params, gradients, world_size=4, learning_rate=0.01
)

# Verify shards reconstruct full params
reconstructed = np.concatenate([s.param_shard for s in shards])
assert np.allclose(reconstructed, new_params)

# AllReduce for DDP
grads = [np.random.randn(100) for _ in range(4)]
synced = AllReduce.mean(grads)  # All devices get the same averaged gradient
```

## Dependencies

- `numpy` (core dependency, already in codomyrmex)
- No PyTorch, NCCL, or distributed runtime required
