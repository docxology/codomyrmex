# Eval Harness -- Technical Specification

## Architecture

### Evaluation Pipeline

```
EvalTask (name + examples + metric)
    -> EvalHarness.evaluate_task()
    -> For each example: model_fn(input) -> prediction
    -> Metric.score(predictions, targets) -> float
    -> EvalResult (score, latency, details)
```

### Normalization

All text comparison uses `normalize_answer()`:
1. Strip leading/trailing whitespace
2. Convert to lowercase

### ExactMatch Metric

```
score = sum(normalize(pred_i) == normalize(target_i)) / N
```

### F1 Metric (Token-Level)

For each prediction-target pair:
1. Tokenize by whitespace after normalization
2. Compute shared tokens: `common = set(pred_tokens) & set(target_tokens)`
3. Precision = |common| / |pred_tokens|
4. Recall = |common| / |target_tokens|
5. F1 = 2 * precision * recall / (precision + recall)

Final score = mean F1 across all examples.

### Edge Cases

| Case | ExactMatch | F1 |
|------|------------|-----|
| Empty predictions | 0.0 if target non-empty | 0.0 |
| Empty targets | 0.0 | 0.0 |
| Both empty | 1.0 (after normalize) | 1.0 |
| No shared tokens | 0.0 | 0.0 |

### Latency Tracking

Each example's latency is measured with `time.perf_counter()` in milliseconds. The result includes `latency_ms_mean` across all examples in the task.

## Limitations

- Single-threaded evaluation (no parallel model calls)
- No support for multi-turn or conversational evaluation
- F1 uses simple whitespace tokenization (no BPE or wordpiece)
