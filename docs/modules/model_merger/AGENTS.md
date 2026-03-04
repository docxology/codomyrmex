# Model Merger -- Agent Coordination

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides SLERP interpolation and model soup techniques for merging neural network parameter sets. Supports both pairwise model merging and multi-model averaging with configurable weights.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `merge_models` | Merge two model parameter sets using SLERP or linear interpolation | Standard | model_merger |
| `create_model_soup` | Create a model soup by averaging multiple model parameter sets | Standard | model_merger |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Merge fine-tuned model checkpoints into combined models |
| VERIFY | QA Agent | Validate merged model parameter shapes and interpolation weights |


## Agent Instructions

1. Alpha=0.5 gives equal weight to both models; 0.0 = model A only, 1.0 = model B only
2. model_soup accepts optional weights list; uniform averaging if omitted


## Navigation

- [Source README](../../src/codomyrmex/model_merger/README.md) | [SPEC.md](SPEC.md)
