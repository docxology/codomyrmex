# Prompt Engineering Testing -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Framework for evaluating prompt output quality through configurable evaluators, test suites, A/B testing of prompt variants, and regression detection between test runs.

## Architecture

Three-layer design: models (data classes for test cases and results), evaluators (strategy pattern with an `Evaluator` ABC and seven concrete implementations), and runners (`PromptTester` for single-variant execution, `ABTest` for multi-variant comparison). Evaluators are pluggable and registered by `EvaluationType` enum.

## Key Classes

### `PromptTestCase` (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique test case identifier |
| `prompt` | `str` | The prompt to send to the executor |
| `expected_output` | `str` | Reference output for exact/similarity matching |
| `evaluation_type` | `EvaluationType` | Which evaluator strategy to use |
| `expected_contains` | `list[str]` | Substrings that must appear in the output |
| `expected_not_contains` | `list[str]` | Substrings that must not appear |
| `weight` | `float` | Relative importance (default 1.0) |

### `TestSuiteResult` (dataclass)

| Property / Method | Returns | Description |
|-------------------|---------|-------------|
| `pass_rate` | `float` | Fraction of tests passed |
| `average_score` | `float` | Mean evaluator score across all results |
| `median_score` | `float` | Median evaluator score |
| `average_latency_ms` | `float` | Mean execution latency |
| `worst_tests(n)` | `list[TestResult]` | N lowest-scoring tests |
| `score_distribution(buckets)` | `dict[str, int]` | Histogram of scores |
| `regression_check(baseline, threshold)` | `dict` | Detect regressions vs. a baseline run |
| `markdown()` | `str` | Formatted markdown report |

### Evaluators

| Class | Strategy | Score Semantics |
|-------|----------|----------------|
| `ExactMatchEvaluator` | Binary exact string match | 0.0 or 1.0 |
| `ContainsEvaluator` | Substring containment | Fraction of checks passed |
| `SimilarityEvaluator` | Word-level Jaccard index | 0.0 to 1.0 |
| `LengthEvaluator` | Output length within bounds | Proportional penalty outside bounds |
| `RegexEvaluator` | Regex pattern matching | Fraction of patterns matched |
| `CompositeEvaluator` | Weighted combination | Weighted average of sub-evaluators |
| `CustomEvaluator` | User-provided function | Function return value |

### `PromptTester`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `run` | `suite: PromptTestSuite, executor: Callable[[str], str], prompt_version: str` | `TestSuiteResult` | Execute all test cases with evaluators |
| `register_evaluator` | `eval_type: EvaluationType, evaluator: Evaluator` | `None` | Register custom evaluator |

### `ABTest`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_variant` | `name: str, prompt_template: str` | `ABTest` | Add a prompt variant |
| `run` | `suite, executor_factory` | `dict[str, TestSuiteResult]` | Run all variants |
| `get_winner` | `metric: str` | `str\|None` | Name of best variant by metric |
| `compare` | | `dict[str, dict]` | Side-by-side metric comparison |

## Dependencies

- **Internal**: None (self-contained submodule)
- **External**: `re`, `time`, `statistics`, `datetime`, `abc` (stdlib)

## Constraints

- All evaluator scores must be in the range [0.0, 1.0].
- `PromptTester` default pass threshold is 0.5; configurable at construction.
- `regression_check` uses a threshold of 0.05 by default for both pass_rate and score deltas.
- `ABTest.get_winner` treats `average_latency_ms` as lower-is-better; all other metrics as higher-is-better.
- Zero-mock: real executor function calls only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Executor exceptions during `_run_test` are caught and produce `TestStatus.ERROR` results with the error message preserved.
- All errors logged before propagation.
