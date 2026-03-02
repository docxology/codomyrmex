# Distributed Training -- Technical Specification

## Architecture

### FSDP (Fully Sharded Data Parallel)

FSDP shards model parameters across devices to reduce per-device memory:

**Forward pass:**
1. AllGather: reconstruct full params from shards
2. Compute forward pass with full params
3. Free gathered params (only keep local shard)

**Backward pass:**
1. AllGather again for gradient computation
2. Compute local gradients
3. ReduceScatter: sum gradients, scatter shards back

### DDP (Distributed Data Parallel)

DDP replicates full model on each device:
1. Each device processes a different data batch
2. AllReduce: sum (or average) gradients across all devices
3. Each device applies the same update

### Collective Operations

| Operation | Input | Output | Communication |
|-----------|-------|--------|---------------|
| AllGather | Shards | Full tensor on all devices | All-to-All |
| ReduceScatter | Full tensors | Reduced shards | All-to-All |
| AllReduce (sum) | Tensors | Summed tensor on all | Ring |
| AllReduce (mean) | Tensors | Averaged tensor on all | Ring |

### Optimizer Step Simulation

```
mean_grad = average(gradients across devices)
new_params = params - learning_rate * mean_grad
shards = split(new_params, world_size)
```

## Limitations

- Simulates communication semantics, not actual latency or bandwidth
- 1D parameter vectors only (no multi-dimensional sharding)
- No mixed precision, gradient scaling, or gradient checkpointing
- CPU only (NumPy)
