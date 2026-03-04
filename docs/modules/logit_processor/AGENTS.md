# Logit Processor -- Agent Coordination

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides sampling strategies for language model outputs including temperature scaling, top-k filtering, nucleus (top-p) sampling, and repetition penalty. Implements a composable processor pipeline for token sampling.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `process_logits` | Apply sampling strategies to language model logits and return sampled token | Standard | logit_processor |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| EXECUTE | Engineer Agent | Apply configurable sampling strategies to LLM output logits |
| BUILD | Engineer Agent | Compose logit processor chains for custom generation behavior |


## Agent Instructions

1. Temperature > 1.0 increases diversity; < 1.0 focuses on high-probability tokens
2. top_k=0 disables top-k filtering; top_p=1.0 disables nucleus sampling
3. Set seed for reproducible sampling results


## Navigation

- [Source README](../../src/codomyrmex/logit_processor/README.md) | [SPEC.md](SPEC.md)
