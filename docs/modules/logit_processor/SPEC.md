# Logit Processor Specification

**Version**: v1.1.6 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides sampling strategies for language model outputs including temperature scaling, top-k filtering, nucleus (top-p) sampling, and repetition penalty. Implements a composable processor pipeline for token sampling.

## Functional Requirements

1. Temperature scaling for controlling output diversity
2. Top-k filtering to restrict sampling to the k most likely tokens
3. Nucleus (top-p) sampling with cumulative probability threshold
4. Repetition penalty to discourage previously generated tokens


## Interface

```python
from codomyrmex.logit_processor import TemperatureProcessor, TopKProcessor, TopPProcessor, LogitProcessorList, sample_token

processors = LogitProcessorList([TemperatureProcessor(0.8), TopKProcessor(50)])
token_id = sample_token(logits, temperature=0.8, top_k=50)
```

## Exports

LogitProcessor, LogitProcessorList, TemperatureProcessor, TopKProcessor, TopPProcessor, RepetitionPenaltyProcessor, greedy_decode, sample_token

## Navigation

- [Source README](../../src/codomyrmex/logit_processor/README.md) | [AGENTS.md](AGENTS.md)
