# Logit Processor - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `logit_processor` module provides composable sampling strategies for language model outputs. Processors modify logit distributions before token selection, supporting temperature scaling, top-k, nucleus (top-p), and repetition penalty.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `LogitProcessor` | Abstract base class for logit processors |
| `TemperatureProcessor` | Scale logits to control randomness (< 1.0 sharper, > 1.0 flatter) |
| `TopKProcessor` | Keep only the k highest-scoring tokens |
| `TopPProcessor` | Nucleus sampling — cumulative probability cutoff |
| `RepetitionPenaltyProcessor` | Penalise previously generated tokens to reduce repetition |
| `LogitProcessorList` | Chain multiple processors in sequence |

### 2.2 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `sample_token` | `(logits, temperature, top_k, top_p, repetition_penalty, input_ids, seed) -> int` | One-call sampling with configurable strategy |
| `greedy_decode` | `(logits) -> int` | Return argmax token (greedy decoding) |

## 3. MCP Tools

Available via `mcp_tools.py` for agent-driven logit processing operations.

## 4. Usage Example

```python
from codomyrmex.logit_processor import sample_token, TemperatureProcessor, TopKProcessor
import numpy as np

logits = np.random.randn(50257)

# Quick sampling
token = sample_token(logits, temperature=0.8, top_k=50, top_p=0.9, seed=42)

# Manual processor chain
temp = TemperatureProcessor(0.7)
topk = TopKProcessor(40)
processed = topk(temp(logits))
```

## 5. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md) | [MCP Tools](MCP_TOOL_SPECIFICATION.md)
