# Agent Guidelines -- Distributed Training

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Distributed Training provides FSDP and DDP simulation for understanding distributed training
mechanics. Simulates parameter sharding, AllGather, ReduceScatter, and AllReduce collective
operations using pure NumPy. One MCP tool (`fsdp_simulate_step`) exposes the simulation to
PAI agents.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `FSDPShard`, `AllReduce`, `simulate_fsdp_step` |
| `fsdp.py` | Core FSDP/DDP simulation (sharding, collectives, optimizer step) |
| `mcp_tools.py` | MCP tool: `fsdp_simulate_step` |

## Key Classes

- **FSDPShard** -- Dataclass representing one device's parameter and gradient shard
- **AllReduce** -- Static methods for sum and mean gradient synchronization (DDP)
- **all_gather** -- Concatenate shards to reconstruct full tensor
- **reduce_scatter** -- Split gradient into averaged shards
- **simulate_fsdp_step** -- Full FSDP optimizer step simulation

## Agent Instructions

1. **Simulate FSDP** -- Use `simulate_fsdp_step(params, grads, world_size)` for a full step
2. **AllGather** -- Use `all_gather(shards)` to reconstruct full parameters from shards
3. **ReduceScatter** -- Use `reduce_scatter(grad, world_size)` for gradient sharding
4. **AllReduce** -- Use `AllReduce.mean(grads)` for DDP-style gradient sync

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `fsdp_simulate_step` | Simulate one FSDP distributed training step | SAFE |

## Operating Contracts

- `FSDPShard.grad_shard` defaults to zeros if not provided
- `all_gather` concatenates along axis 0 (1D shards expected)
- `reduce_scatter` divides by world_size (averaging, not summing)
- `AllReduce` returns independent copies (mutating one does not affect others)
- `simulate_fsdp_step` uses simple SGD: params -= lr * mean_grad

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full simulation | `fsdp_simulate_step` | SAFE |
| **Architect** | Scaling analysis | `fsdp_simulate_step` -- world_size experiments | SAFE |
| **QATester** | Verification | `fsdp_simulate_step` -- shard coverage checks | SAFE |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
