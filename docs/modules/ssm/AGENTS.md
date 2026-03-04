# State Space Models -- Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements Mamba selective State Space Model (SSM) from scratch. Provides MambaBlock with selective scan mechanism for efficient sequence modeling as an alternative to attention-based transformers.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `ssm_forward` | Run a forward pass through Mamba State Space Model | Standard | ssm |
| `flash_attention_forward` | Run Flash Attention and verify against standard attention | Standard | neural |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Construct and evaluate SSM-based sequence models |
| VERIFY | QA Agent | Validate SSM output shapes and selective scan behavior |


## Agent Instructions

1. d_state controls the SSM hidden state dimension (higher = more expressive but slower)
2. Stack multiple MambaBlock layers via n_layers parameter for deeper models


## Navigation

- [Source README](../../src/codomyrmex/ssm/README.md) | [SPEC.md](SPEC.md)
