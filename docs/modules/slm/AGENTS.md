# Small Language Model -- Agent Coordination

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements a tiny GPT-2 style transformer for on-device inference. Provides configurable model architecture with token generation and forward pass capabilities in pure NumPy.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `slm_generate` | Generate tokens from a tiny language model given a prompt | Standard | slm |
| `slm_forward` | Run a forward pass through the SLM and return logit statistics | Standard | slm |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Construct and run small language models for local inference |
| VERIFY | QA Agent | Validate model output shapes and logit distributions |


## Agent Instructions

1. Configure model with vocab_size, d_model, n_heads, n_layers, d_ff, and max_seq_len
2. slm_generate produces token sequences autoregressively from a prompt


## Navigation

- [Source README](../../src/codomyrmex/slm/README.md) | [SPEC.md](SPEC.md)
