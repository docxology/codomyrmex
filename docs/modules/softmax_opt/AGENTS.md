# Softmax Optimization -- Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides numerically stable softmax implementations including standard softmax, log-softmax, online softmax (single-pass algorithm), and safe softmax with overflow prevention.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `compute_softmax` | Compute softmax probabilities from logits with temperature and variant selection | Standard | softmax_opt |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Apply optimized softmax implementations in model computations |
| VERIFY | QA Agent | Validate numerical stability and probability sum invariants |


## Agent Instructions

1. Supported variants: 'standard' (with temperature), 'log', and 'online' (single-pass)
2. Temperature > 1.0 produces more uniform distributions; < 1.0 produces more peaked distributions


## Navigation

- [Source README](../../src/codomyrmex/softmax_opt/README.md) | [SPEC.md](SPEC.md)
