# LLM Eval Harness

Standardized evaluation framework for language models with ExactMatch and F1 metrics.

## Overview

The eval harness provides:

- **EvalTask**: Named evaluation task with input/target example pairs
- **EvalResult**: Per-task results including score, metric, latency, and per-example details
- **ExactMatchMetric**: Binary exact match after normalization (lowercase, strip)
- **F1Metric**: Token-level F1 score (precision/recall over word tokens)
- **EvalHarness**: Orchestrator that runs a model function against multiple tasks

## Quick Start

```python
from codomyrmex.eval_harness import EvalHarness, EvalTask

# Define tasks
task = EvalTask(
    name="capitals",
    examples=[
        {"input": "What is the capital of France?", "target": "Paris"},
        {"input": "What is the capital of Japan?", "target": "Tokyo"},
    ],
    metric="exact_match",
)

# Evaluate with a model function
def my_model(text: str) -> str:
    # Your model here
    return "Paris" if "France" in text else "Unknown"

harness = EvalHarness(model_fn=my_model)
result = harness.evaluate_task(task)
print(result.score)  # 0.5 (1 out of 2 correct)
```

## Metrics

### ExactMatch
Normalizes predictions and targets (lowercase + strip), then checks equality. Score = fraction of exact matches.

### F1
Token-level F1: split prediction and target into words, compute precision and recall over shared tokens. Score = mean F1 across examples.

## Dependencies

- `numpy` (core dependency)
- No external evaluation libraries
