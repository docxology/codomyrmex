# Personal AI Infrastructure -- Distributed Training Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Distributed Training provides FSDP and DDP simulation for PAI agents. It enables understanding of distributed training mechanics (parameter sharding, gradient synchronization) using pure Python + NumPy, without requiring actual multi-GPU hardware.

## PAI Algorithm Phase Mapping

| Phase | Activity | Key Functions/Tools |
|-------|----------|-------------------|
| **OBSERVE** | Analyze model size and device count requirements | `FSDPShard`, shard size calculations |
| **THINK** | Evaluate FSDP vs DDP trade-offs for model scale | `AllReduce` vs `reduce_scatter` comparison |
| **PLAN** | Configure world_size and sharding strategy | `simulate_fsdp_step` parameters |
| **BUILD** | Set up distributed training simulation | `FSDPShard`, `AllReduce` |
| **EXECUTE** | Run simulated FSDP optimizer steps | `simulate_fsdp_step`, `all_gather`, `reduce_scatter` |
| **VERIFY** | Validate shard coverage and gradient sync correctness | Shard reconstruction, AllReduce consistency |
| **LEARN** | Record scaling metrics (norm before/after, grad norm) | `fsdp_simulate_step` MCP tool results |

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `fsdp_simulate_step` | Simulate one FSDP step with configurable world_size | SAFE |

## Agent Capabilities

| Agent Type | Primary Use | Key Functions |
|-----------|-------------|--------------|
| **Engineer** | Simulate and validate distributed training steps | `simulate_fsdp_step`, `AllReduce` |
| **Architect** | Analyze scaling behavior and memory trade-offs | `fsdp_simulate_step` |
| **QATester** | Verify collective operation correctness | `all_gather`, `reduce_scatter`, shard checks |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
