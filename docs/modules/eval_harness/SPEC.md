# LLM Eval Harness Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides a standardized evaluation framework for language models. Defines evaluation tasks with input-target pairs and supports exact match and F1 scoring metrics for systematic model benchmarking.

## Functional Requirements

1. Define evaluation tasks as EvalTask with named examples containing input-target pairs
2. ExactMatchMetric for strict string comparison scoring
3. F1Metric for token-level precision/recall scoring on prediction-target pairs


## Interface

```python
from codomyrmex.eval_harness import EvalHarness, EvalTask, ExactMatchMetric, F1Metric

harness = EvalHarness()
task = EvalTask(name="qa", examples=[{"input": "q", "target": "a"}], metric="exact_match")
result = harness.evaluate_all([task])
```

## Exports

EvalHarness, EvalTask, EvalResult, ExactMatchMetric, F1Metric

## Navigation

- [Source README](../../src/codomyrmex/eval_harness/README.md) | [AGENTS.md](AGENTS.md)
