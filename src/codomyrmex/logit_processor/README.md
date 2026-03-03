# Logit Processor Module

This module provides composable processors that modify logit distributions before token sampling, commonly used in language model inference pipelines.

## Processors

- **TemperatureProcessor**: Scale logits to control randomness.
- **TopKProcessor**: Keep only the *k* highest-scoring tokens.
- **TopPProcessor**: Nucleus sampling (cumulative probability cutoff).
- **RepetitionPenaltyProcessor**: Penalize previously generated tokens.
- **LogitProcessorList**: Chain multiple processors in sequence.

## APIs

Convenience functions `sample_token` and `greedy_decode` combine these into single-call sampling APIs.

### Example

```python
from codomyrmex.logit_processor import sample_token

logits = [1.0, 5.0, 2.0, 0.1]
token = sample_token(logits, temperature=0.7, top_k=50, top_p=0.9)
```

## MCP Tools

The module exposes `process_logits` as an MCP tool for agent-driven token sampling.
