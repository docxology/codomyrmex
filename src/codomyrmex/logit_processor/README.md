# Logit Processor Module

**Version**: v0.1.0 | **Status**: Development | **Last Updated**: March 2026

## Overview

The `logit_processor` module provides tools for adjusting token probabilities during language model generation, enabling advanced sampling strategies like temperature scaling, top-k filtering, and custom constraints.

## Capabilities

- Temperature Scaling
- Top-K and Top-P (Nucleus) Filtering
- Repetition Penalties
- Custom Logit Biases

## Getting Started

```python
from codomyrmex.logit_processor import TopKProcessor

processor = TopKProcessor(k=50)
adjusted_logits = processor.process(input_logits)
```

## Documentation

- [AGENTS](AGENTS.md)
- [SPEC](SPEC.md)
