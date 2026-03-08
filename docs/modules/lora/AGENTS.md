# LoRA (Low-Rank Adaptation) -- Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements Low-Rank Adaptation (LoRA) for parameter-efficient fine-tuning. Decomposes weight update matrices into low-rank factors, enabling fine-tuning with a fraction of the original parameters.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `lora_apply` | Apply LoRA decomposition to a weight matrix and report parameter reduction | Standard | lora |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Apply LoRA adapters to model weight matrices for efficient fine-tuning |
| VERIFY | QA Agent | Verify parameter reduction and adaptation quality |


## Agent Instructions

1. Rank r should be much smaller than min(d, k) for meaningful parameter reduction
2. Alpha controls the scaling of the LoRA delta (scaling = alpha / rank)


## Navigation

- [Source README](../../src/codomyrmex/lora/README.md) | [SPEC.md](SPEC.md)
