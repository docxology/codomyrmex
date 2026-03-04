# Distributed Training Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Simulates FSDP (Fully Sharded Data Parallel) and tensor parallelism for distributed neural network training. Provides parameter sharding, all-reduce gradient aggregation, and multi-device training step simulation.

## Functional Requirements

1. Fully Sharded Data Parallelism (FSDP) with parameter partitioning across devices
2. All-reduce gradient aggregation across worker shards with mean reduction
3. Single-step training simulation with SGD parameter update


## Interface

```python
from codomyrmex.distributed_training import FSDPShard, AllReduce, simulate_fsdp_step

new_params, shards = simulate_fsdp_step(
    params, gradients, world_size=4, learning_rate=0.01
)
```

## Exports

FSDPShard, AllReduce, simulate_fsdp_step

## Navigation

- [Source README](../../src/codomyrmex/distributed_training/README.md) | [AGENTS.md](AGENTS.md)
