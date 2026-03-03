# Logit Processor

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Logit processing and token sampling utilities for LLM inference pipelines. Provides composable processor classes for temperature scaling, top-k filtering, nucleus (top-p) sampling, and repetition penalty. Includes convenience functions for single-call sampling and greedy decoding.

## Installation

```bash
uv sync
```

The module depends on `numpy`, which is included in the core Codomyrmex dependencies. No additional extras required.

## Quick Start

### Greedy Decoding

```python
import numpy as np
from codomyrmex.logit_processor import greedy_decode

logits = np.array([1.0, 3.5, 2.0, 0.5])
token_id = greedy_decode(logits)  # Returns 1 (index of highest logit)
```

### Controlled Sampling

```python
from codomyrmex.logit_processor import sample_token
import numpy as np

logits = np.array([1.0, 3.5, 2.0, 0.5, 1.2])
token_id = sample_token(
    logits,
    temperature=0.7,
    top_k=3,
    top_p=0.9,
    repetition_penalty=1.3,
    input_ids=[1, 1, 3],  # Previously generated tokens
    seed=42,
)
```

### Composable Processor Pipeline

```python
from codomyrmex.logit_processor import (
    TemperatureProcessor,
    TopKProcessor,
    TopPProcessor,
    RepetitionPenaltyProcessor,
    LogitProcessorList,
)
import numpy as np

pipeline = LogitProcessorList([
    RepetitionPenaltyProcessor(penalty=1.3),
    TemperatureProcessor(temperature=0.8),
    TopKProcessor(top_k=40),
    TopPProcessor(top_p=0.95),
])

logits = np.random.randn(50000)  # Simulated vocab-sized logits
processed = pipeline(logits, input_ids=[10, 20, 10])
```

## Key Concepts

### Processor Chain

Logit processors are applied sequentially. The standard order is:

1. **RepetitionPenaltyProcessor** -- penalize previously generated tokens
2. **TemperatureProcessor** -- scale logits to control randomness
3. **TopKProcessor** -- keep only the k highest-scoring tokens
4. **TopPProcessor** -- nucleus sampling (cumulative probability cutoff)

Each processor takes a `numpy` array of logits and returns a modified array of the same shape.

### Temperature

- `temperature < 1.0`: Sharper distribution (more confident, less random)
- `temperature = 1.0`: No change
- `temperature > 1.0`: Flatter distribution (more diverse, more random)

### Repetition Penalty

For logits > 0, the logit is divided by the penalty. For logits < 0, the logit is multiplied by the penalty. This reduces the probability of tokens that appear in `input_ids`.

## Core Classes

| Class | Description |
|-------|-------------|
| `LogitProcessor` | Abstract base class for all processors |
| `TemperatureProcessor` | Scale logits by temperature |
| `TopKProcessor` | Keep only top-k logits, set rest to -inf |
| `TopPProcessor` | Nucleus sampling -- keep tokens until cumulative probability reaches p |
| `RepetitionPenaltyProcessor` | Penalize previously generated tokens |
| `LogitProcessorList` | Chain multiple processors in sequence |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `sample_token(logits, ...)` | Apply processors and sample a token from the resulting distribution |
| `greedy_decode(logits)` | Return the argmax token (deterministic) |

## MCP Tools

This module exposes one MCP tool via `mcp_tools.py`:

| Tool | Description |
|------|-------------|
| `process_logits` | Sample a token from logits with temperature, top-k, top-p, and repetition penalty. Returns `sampled_token`, `greedy_token`, `top5_tokens`, and `entropy`. |

## API Reference

See the source code in `processor.py` for full docstrings and parameter details.

## Integration

The logit processor module sits in the **Core Layer** of Codomyrmex and pairs with the `llm` module for end-to-end inference pipelines. It provides the sampling logic that sits between raw model output (logits) and final token selection.

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/logit_processor/
```

## Navigation Links

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README.md](../../../README.md)
- **Agent Guide**: [AGENTS.md](AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)
- **PAI Integration**: [PAI.md](PAI.md)
