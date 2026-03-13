# Eval Harness - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `eval_harness` module provides a standardised evaluation framework for language models. Supports custom tasks with pluggable metrics for benchmarking model performance.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `EvalHarness` | Orchestrates evaluation runs across multiple tasks and metrics |
| `EvalTask` | Definition of an evaluation task (dataset, prompts, expected outputs) |
| `EvalResult` | Aggregated results from an evaluation run |
| `ExactMatchMetric` | Metric computing exact string match accuracy |
| `F1Metric` | Metric computing token-level F1 score |

## 3. Usage Example

```python
from codomyrmex.eval_harness import EvalHarness, EvalTask, ExactMatchMetric

task = EvalTask(name="qa", prompts=["What is 2+2?"], expected=["4"])
harness = EvalHarness(tasks=[task], metrics=[ExactMatchMetric()])

results = harness.run(model_fn=lambda p: "4")
print(results.scores)
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
