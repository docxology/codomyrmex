# Codomyrmex Agents -- src/codomyrmex/prompt_engineering/testing

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides a framework for evaluating prompt quality through test suites, multiple evaluator strategies (exact match, contains, similarity, regex, composite), A/B testing of prompt variants, and regression detection across test runs.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `PromptTestCase` | Dataclass defining a single test case with expected output, contains/not-contains lists, and weight |
| `models.py` | `TestResult` | Dataclass capturing actual output, score (0-1), latency, and pass/fail status |
| `models.py` | `TestSuiteResult` | Aggregate result with pass_rate, average/median score, latency stats, score distribution, regression checking, and markdown report generation |
| `models.py` | `EvaluationType` | Enum: EXACT_MATCH, CONTAINS, NOT_CONTAINS, SEMANTIC, CUSTOM |
| `models.py` | `TestStatus` | Enum: PENDING, RUNNING, PASSED, FAILED, ERROR |
| `evaluators.py` | `Evaluator` | Abstract base class with `evaluate(test_case, actual_output) -> float` |
| `evaluators.py` | `ExactMatchEvaluator` | Binary 0/1 scoring with optional case sensitivity |
| `evaluators.py` | `ContainsEvaluator` | Fractional score based on substring containment checks |
| `evaluators.py` | `SimilarityEvaluator` | Word-level Jaccard index for fuzzy comparison |
| `evaluators.py` | `LengthEvaluator` | Score based on output length within min/max bounds |
| `evaluators.py` | `RegexEvaluator` | Score against one or more compiled regex patterns |
| `evaluators.py` | `CompositeEvaluator` | Weighted combination of multiple evaluators |
| `evaluators.py` | `CustomEvaluator` | User-provided scoring function wrapper |
| `runner.py` | `PromptTestSuite` | Collection of `PromptTestCase` instances with add/get operations |
| `runner.py` | `PromptTester` | Main test runner: executes prompts via a user-provided executor, evaluates with registered evaluators |
| `runner.py` | `ABTest` | A/B testing engine comparing multiple prompt variants with a winner metric |

## Operating Contracts

- All evaluators return a float in the range [0.0, 1.0] where 1.0 is a perfect match.
- `PromptTester.run` calls the user-provided `executor(prompt) -> str` function for each test case; exceptions produce `TestStatus.ERROR` results.
- Pass threshold defaults to 0.5; scores >= threshold yield PASSED, below yield FAILED.
- `TestSuiteResult.regression_check` compares against a baseline with a configurable threshold (default 0.05).
- `ABTest.get_winner` supports metrics: `pass_rate`, `average_score`, `average_latency_ms` (lower is better for latency).
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: No external codomyrmex modules; self-contained
- **Used by**: Prompt engineering workflows, CI prompt quality gates

## Navigation

- **Parent**: [prompt_engineering](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
