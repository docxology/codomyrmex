# Knowledge Distillation -- Agent Coordination

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements teacher-student knowledge distillation training pipeline. Computes distillation loss combining soft-label KL divergence with hard-label cross-entropy for model compression.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `distillation_compute_loss` | Compute knowledge distillation loss on synthetic teacher-student data | Standard | distillation |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Train smaller student models from larger teacher models |
| VERIFY | QA Agent | Validate distillation loss convergence and student quality |


## Agent Instructions

1. Set temperature > 1.0 for softer probability distributions (typical range 2.0-20.0)
2. Alpha controls the weight between distillation loss and hard-label cross-entropy loss


## Navigation

- [Source README](../../src/codomyrmex/distillation/README.md) | [SPEC.md](SPEC.md)
