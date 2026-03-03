# Logit Processor -- Agent Integration Guide

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## What Agents Can Do With This Module

The logit processor module provides token sampling and logit manipulation utilities for LLM inference. Agents can use it to control how tokens are selected from model output distributions, enabling fine-grained control over generation behavior (temperature, top-k, top-p, repetition penalty).

### Capabilities

| Capability | Class / Function | Description |
|------------|-----------------|-------------|
| Token sampling | `sample_token()` | Sample next token with configurable strategies |
| Greedy decoding | `greedy_decode()` | Deterministic argmax token selection |
| Temperature scaling | `TemperatureProcessor` | Control randomness of output distribution |
| Top-k filtering | `TopKProcessor` | Restrict sampling to top k tokens |
| Nucleus sampling | `TopPProcessor` | Restrict sampling to cumulative probability threshold |
| Repetition penalty | `RepetitionPenaltyProcessor` | Reduce probability of previously generated tokens |
| Pipeline composition | `LogitProcessorList` | Chain multiple processors in sequence |

## Available MCP Tools

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `process_logits` | Apply sampling strategies to language model logits. Returns sampled token, greedy token, top-5 tokens with probabilities, and entropy. | SAFE |

### process_logits Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `logits` | `list[float]` | required | Raw logit scores from model |
| `temperature` | `float` | `1.0` | Sampling temperature |
| `top_k` | `int` | `0` | Top-k filtering cutoff (0 = disabled) |
| `top_p` | `float` | `1.0` | Nucleus sampling threshold (1.0 = disabled) |
| `repetition_penalty` | `float` | `1.0` | Penalty for repeated tokens (1.0 = disabled) |
| `previous_tokens` | `list[int]` | `None` | Token history for repetition penalty |
| `seed` | `int` | `None` | Random seed for reproducibility |

### process_logits Response

```json
{
  "status": "success",
  "sampled_token": 42,
  "greedy_token": 42,
  "top5_tokens": [
    {"id": 42, "prob": 0.35},
    {"id": 17, "prob": 0.22},
    {"id": 89, "prob": 0.15},
    {"id": 3, "prob": 0.08},
    {"id": 201, "prob": 0.05}
  ],
  "entropy": 2.31
}
```

## Agent Workflow Patterns

### Pattern 1: Controlled Token Sampling via MCP

```python
# Agent calls process_logits MCP tool with specific sampling parameters
result = process_logits(
    logits=[1.2, 3.5, 0.8, 2.1, -0.5],
    temperature=0.7,
    top_k=3,
    seed=42,
)
# result["sampled_token"] -> selected token ID
# result["entropy"] -> distribution entropy for confidence assessment
```

### Pattern 2: Composable Processor Pipeline (Python)

```python
from codomyrmex.logit_processor import (
    TemperatureProcessor,
    TopKProcessor,
    LogitProcessorList,
    sample_token,
)
import numpy as np

pipeline = LogitProcessorList([
    TemperatureProcessor(temperature=0.8),
    TopKProcessor(top_k=50),
])

logits = np.array([...])  # Raw model output
processed = pipeline(logits)
```

### Pattern 3: Entropy-Based Confidence Check

```python
result = process_logits(logits=raw_logits, temperature=1.0)
if result["entropy"] > 4.0:
    # High entropy = model is uncertain, consider re-prompting
    pass
elif result["entropy"] < 1.0:
    # Low entropy = model is confident
    pass
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `process_logits` -- token sampling for inference pipelines | SAFE |
| **Architect** | Read + Design | `process_logits` -- evaluate sampling strategies, analyze entropy | SAFE |
| **QATester** | Validation | `process_logits` -- verify sampling correctness, test reproducibility with seeds | SAFE |
| **Researcher** | Read-only | `process_logits` -- analyze token distributions, measure entropy | SAFE |

### Engineer Agent
**Access**: Full -- all processors, sampling functions, and MCP tool.
**Use Cases**: Building inference pipelines, configuring sampling parameters for code generation tasks, integrating with the `llm` module for end-to-end generation.

### Architect Agent
**Access**: Read + Design -- analyze sampling behavior, compare strategies.
**Use Cases**: Designing sampling strategies for different use cases (creative vs. deterministic), evaluating temperature and top-k/top-p trade-offs for system design.

### QATester Agent
**Access**: Validation -- test sampling correctness and reproducibility.
**Use Cases**: Verifying that seeded sampling produces deterministic results, validating that processor chain order produces expected distributions, regression testing sampling behavior.

### Researcher Agent
**Access**: Read-only -- analyze distributions and entropy.
**Use Cases**: Measuring model confidence via entropy, comparing token distributions across different sampling parameters, analyzing repetition penalty effects.

## Integration with PAI Algorithm Phases

| Phase | Usage | Description |
|-------|-------|-------------|
| EXECUTE | `process_logits` / `sample_token` | Sample tokens during LLM inference in automated pipelines |
| EXECUTE | `greedy_decode` | Deterministic token selection for consistent outputs |
| VERIFY | `process_logits` (entropy) | Assess model confidence via entropy measurement |

## Security Constraints

1. **Read-only operations**: All logit processing is purely computational with no side effects. No trust elevation required.
2. **No model access**: This module processes logits, not models. It does not load, download, or execute LLM models.
3. **Reproducibility**: The `seed` parameter enables deterministic sampling for auditability.

## Navigation Links

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README.md](../../../README.md)
- **Module README**: [README.md](README.md)
- **Specification**: [SPEC.md](SPEC.md)
- **PAI Integration**: [PAI.md](PAI.md)
