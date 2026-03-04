# Distributed Training -- Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Simulates FSDP (Fully Sharded Data Parallel) and tensor parallelism for distributed neural network training. Provides parameter sharding, all-reduce gradient aggregation, and multi-device training step simulation.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `fsdp_simulate_step` | Simulate one FSDP distributed training step with parameter sharding | Standard | distributed_training |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Configure and simulate distributed training across multiple devices |
| OBSERVE | Monitoring Agent | Monitor gradient norms and parameter convergence across shards |


## Agent Instructions

1. Set world_size to the number of simulated GPU devices for sharding
2. Parameter size should match the model layer dimensions being distributed


## Navigation

- [Source README](../../src/codomyrmex/distributed_training/README.md) | [SPEC.md](SPEC.md)
