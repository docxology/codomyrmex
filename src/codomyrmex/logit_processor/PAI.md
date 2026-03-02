# Personal AI Infrastructure -- Logit Processor Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Logit processing and token sampling utilities for LLM inference pipelines. Supports temperature scaling, top-k/top-p filtering, repetition penalty, and entropy calculation. Exposes one MCP tool for agent-driven token sampling.

## PAI Capabilities

### Token Sampling

```python
from codomyrmex.logit_processor import greedy_decode, sample_token

# Greedy decoding
token = greedy_decode(logits)

# Controlled sampling with parameters
token = sample_token(logits, temperature=0.7, top_k=50, top_p=0.9)
```

## MCP Tools (Auto-discovered)

| Tool            | Description                                                    |
|-----------------|----------------------------------------------------------------|
| process_logits  | Sample a token from logits with temperature, top-k, top-p, repetition penalty. Returns sampled_token, greedy_token, top5_tokens, entropy. |

### process_logits Parameters

| Parameter         | Type        | Description                          |
|-------------------|-------------|--------------------------------------|
| logits            | list[float] | Raw logit scores from model          |
| temperature       | float       | Sampling temperature                 |
| top_k             | int         | Top-k filtering cutoff               |
| top_p             | float       | Nucleus sampling threshold           |
| repetition_penalty| float       | Penalty for repeated tokens          |
| previous_tokens   | list[int]   | Token history for repetition penalty |
| seed              | int         | Random seed for reproducibility      |

## PAI Phase Mapping

| Phase   | Tool/Function    | Usage                                    |
|---------|------------------|------------------------------------------|
| EXECUTE | process_logits   | Sample tokens during LLM inference       |
| EXECUTE | greedy_decode    | Deterministic token selection             |
| EXECUTE | sample_token     | Stochastic token sampling with controls  |

## Integration Notes

- Has `mcp_tools.py` -- auto-discovered via MCP bridge (1 tool).
- Pairs with `llm` module for end-to-end inference pipelines.
- No trust elevation required -- read-only logit processing.
