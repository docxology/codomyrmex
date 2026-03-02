# Codomyrmex Agents — src/codomyrmex/model_ops/evaluation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Comprehensive model evaluation framework spanning four concerns: output scoring via composable `Scorer` protocols, benchmark suite management for systematic model testing, classification/regression metrics (Accuracy, Precision, Recall, F1, MSE, MAE, RMSE, R-squared, AUC-ROC), and heuristic-based quality analysis across coherence, relevance, completeness, conciseness, and accuracy dimensions.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `scorers.py` | `Scorer` (ABC) | Abstract base for output scorers; defines `score(output, reference) -> float` |
| `scorers.py` | `ExactMatchScorer` | Binary exact-match scoring with case/whitespace options |
| `scorers.py` | `ContainsScorer` | Substring containment check |
| `scorers.py` | `LengthScorer` | Scores output length against a target range with linear decay |
| `scorers.py` | `RegexScorer` | Regex pattern matching (search or full-match mode) |
| `scorers.py` | `CompositeScorer` | Weighted combination of multiple scorers; supports `score_detailed()` |
| `scorers.py` | `create_default_scorer()` | Factory returning a pre-configured `CompositeScorer` |
| `benchmarks.py` | `BenchmarkCase` | Dataclass for a single test case (input, expected output, tags) |
| `benchmarks.py` | `BenchmarkSuite` | Runs cases through a model function, scores with a `Scorer`, returns `SuiteResult` |
| `benchmarks.py` | `SuiteResult` | Aggregated results with `average_score`, `pass_rate`, `to_result()` |
| `metrics.py` | `Metric` (ABC) | Abstract metric with `compute(y_true, y_pred) -> float` |
| `metrics.py` | `ModelEvaluator` | Selects default metrics by `TaskType`, runs evaluation, returns `EvaluationResult` |
| `metrics.py` | `ConfusionMatrix` | Builds and queries a confusion matrix from true/predicted labels |
| `quality.py` | `QualityAnalyzer` | Heuristic quality scorer across five `QualityDimension` values |
| `quality.py` | `QualityReport` | Full report with per-dimension scores, overall weighted average |
| `evaluators.py` | `Evaluator` | Legacy orchestrator running named metric functions over prediction lists |

## Operating Contracts

- All `Scorer.score()` implementations return a `float` in `[0.0, 1.0]`.
- `BenchmarkSuite.run()` catches exceptions from the model function and records `"ERROR: ..."` as the output.
- `CompositeScorer` requires positive weights; `ValueError` raised otherwise.
- `ModelEvaluator` auto-selects metrics based on `TaskType` (classification vs. regression).
- `QualityAnalyzer` requires no LLM calls; all scoring is deterministic heuristic-based.
- Optionally integrates with `codomyrmex.validation.schemas.Result` when available.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.validation.schemas` (optional, for `Result`/`ResultStatus` conversion)
- **Used by**: `model_ops` parent module (re-exports all public symbols)

## Navigation

- **Parent**: [model_ops](../README.md)
- **Root**: [Root](../../../../README.md)
