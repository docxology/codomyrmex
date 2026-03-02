# Model Evaluation — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Four-tier evaluation framework: (1) composable output scorers for comparing model outputs against references, (2) benchmark suites for systematic model testing with timing, (3) classification and regression metrics (Accuracy, Precision, Recall, F1, MSE, MAE, RMSE, R-squared, AUC-ROC, Confusion Matrix), and (4) heuristic quality analysis across coherence, relevance, completeness, conciseness, and accuracy dimensions.

## Architecture

Scorer hierarchy uses an ABC (`Scorer`) with concrete implementations (`ExactMatchScorer`, `ContainsScorer`, `LengthScorer`, `RegexScorer`) composed via `CompositeScorer` with weighted averaging. Metrics follow the same ABC pattern (`Metric`) with `ModelEvaluator` as the orchestrator selecting defaults by `TaskType`. Quality analysis is standalone via `QualityAnalyzer`, using heuristic signals (sentence variance, keyword overlap, completion markers, word frequency, factual density).

## Key Classes

### `Scorer` (ABC) and Implementations

| Class | Method | Parameters | Returns | Description |
|-------|--------|-----------|---------|-------------|
| `Scorer` | `score` | `output: str, reference: str` | `float` | Abstract; returns 0.0-1.0 |
| `Scorer` | `score_batch` | `pairs: list[tuple[str, str]]` | `list[float]` | Batch scoring convenience |
| `ExactMatchScorer` | `score` | `output, reference` | `float` | 1.0 if match, 0.0 otherwise; configurable case/whitespace |
| `LengthScorer` | `score` | `output, reference` | `float` | 1.0 in range, linear decay outside |
| `CompositeScorer` | `score_detailed` | `output, reference` | `dict` | Per-scorer breakdown with weights |

### `BenchmarkSuite`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_case` | `input_text, expected_output, ...` | `BenchmarkCase` | Add a test case |
| `run` | `model_fn: Callable[[str], str], scorer` | `SuiteResult` | Run all cases, time each, aggregate |
| `get_cases_by_tag` | `tag: str` | `list[BenchmarkCase]` | Filter cases by tag |

### `ModelEvaluator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `task_type: TaskType` | — | Auto-selects default metrics |
| `evaluate` | `y_true: list, y_pred: list` | `EvaluationResult` | Compute all metrics, return structured result |
| `add_metric` | `metric: Metric` | `None` | Add a custom metric |

### `QualityAnalyzer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `analyze` | `output: str, context: str` | `QualityReport` | Score across all five dimensions |

## Dependencies

- **Internal**: `codomyrmex.validation.schemas` (optional; `Result`, `ResultStatus`)
- **External**: Standard library only (`math`, `re`, `time`, `uuid`, `collections`, `dataclasses`, `enum`)

## Constraints

- Scores always in `[0.0, 1.0]` range.
- `BenchmarkSuite.run()` swallows model exceptions, recording error strings as output.
- `QualityAnalyzer` is purely heuristic; no LLM calls.
- `BenchmarkResult.passed` threshold is `>= 0.5`.
- `AUCROCMetric` uses Wilcoxon-Mann-Whitney statistic (O(n*m) pairwise comparison).
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `ValueError` raised by `CompositeScorer.add_scorer()` if weight is not positive.
- `ValueError` raised by `LengthScorer` if `min_length < 0` or `max_length < min_length`.
- `ValueError` raised by `create_evaluator()` for unknown task type strings.
- `re.error` caught and logged by `RegexScorer` for invalid patterns (returns 0.0).
- All errors logged before propagation.
