# Logit Processor Module

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `logit_processor` module provides composable processors that modify logit distributions before token sampling during language model text generation. It implements temperature scaling, top-k filtering, nucleus (top-p) sampling, and repetition penalty as chainable processors. Includes convenience functions for greedy decoding and probabilistic token sampling. Pure Python and NumPy -- no PyTorch dependency.

## Architecture

The module uses a processor chain pattern built on an abstract base class:

- **`LogitProcessor`** (ABC) -- base class with `__call__(logits, input_ids)` interface
- **`TemperatureProcessor`** -- scale logits to control randomness
- **`TopKProcessor`** -- keep only the k highest-scoring tokens (set rest to -inf)
- **`TopPProcessor`** -- nucleus sampling: keep tokens until cumulative probability reaches p
- **`RepetitionPenaltyProcessor`** -- penalize previously generated tokens
- **`LogitProcessorList`** -- chain multiple processors in sequence
- **`sample_token()`** and **`greedy_decode()`** -- convenience sampling APIs

## Key Exports

| Export | Module | Description |
|--------|--------|-------------|
| `LogitProcessor` | `processor.py` | Abstract base class for logit processors |
| `LogitProcessorList` | `processor.py` | Chain multiple processors in sequence |
| `TemperatureProcessor` | `processor.py` | Scale logits by temperature (< 1 = sharper, > 1 = flatter) |
| `TopKProcessor` | `processor.py` | Keep only top-k logits, set rest to -inf |
| `TopPProcessor` | `processor.py` | Nucleus sampling with cumulative probability cutoff |
| `RepetitionPenaltyProcessor` | `processor.py` | Reduce probability of repeated tokens |
| `greedy_decode` | `processor.py` | Greedy token selection (argmax) |
| `sample_token` | `processor.py` | Probabilistic sampling with processor chain |

## Quick Start

```python
import numpy as np
from codomyrmex.logit_processor import (
    LogitProcessorList, TemperatureProcessor,
    TopKProcessor, TopPProcessor, RepetitionPenaltyProcessor,
    sample_token
)

# Create a processor chain
processors = LogitProcessorList([
    TemperatureProcessor(temperature=0.8),
    TopKProcessor(top_k=50),
    TopPProcessor(top_p=0.9),
    RepetitionPenaltyProcessor(penalty=1.3),
])

# Apply to raw logits
logits = np.random.randn(32000)  # vocab_size = 32000
previous_tokens = [42, 100, 42, 7]
processed = processors(logits, input_ids=previous_tokens)

# Sample a token
token_id = sample_token(logits, processors=processors, input_ids=previous_tokens)
```

## Processor Behavior

| Processor | Parameter | Effect |
|-----------|-----------|--------|
| Temperature | < 1.0 | Sharper distribution (more confident) |
| Temperature | > 1.0 | Flatter distribution (more random) |
| Top-K | k=50 | Only 50 highest logits have non-zero probability |
| Top-P | p=0.9 | Keep tokens until 90% cumulative probability |
| Repetition | penalty=1.3 | Divide positive logits, multiply negative logits for seen tokens |

## MCP Tools

This module exposes MCP tools via `mcp_tools.py` and is auto-discovered by the PAI MCP bridge.

## PAI Integration

| Phase | Usage |
|-------|-------|
| EXECUTE | Control text generation quality and diversity |
| VERIFY | Compare sampling strategies for output quality |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/logit_processor/ -v
```

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public exports: all 8 symbols |
| `processor.py` | All processor implementations, sampling functions |
| `mcp_tools.py` | MCP tool definitions for PAI bridge |

## Related Modules

- [slm](../slm/) -- Small Language Model that uses logit processors for generation
- [softmax_opt](../softmax_opt/) -- Optimized softmax used in probability computation
- [dpo](../dpo/) -- Alignment training that affects logit distributions

## Navigation

- **AGENTS**: [AGENTS.md](AGENTS.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Source**: [`src/codomyrmex/logit_processor/`](../../../src/codomyrmex/logit_processor/)
- **Parent**: [Module Documentation](../README.md)
- **Root**: [docs/](../../README.md)
