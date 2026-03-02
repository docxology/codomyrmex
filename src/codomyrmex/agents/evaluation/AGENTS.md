# Codomyrmex Agents — src/codomyrmex/agents/evaluation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides a generic benchmarking framework for evaluating and comparing AI agents against test suites, with pluggable scoring strategies, latency measurement, cost tracking, and tag-based result aggregation.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `MetricType` | Enum of metric categories: LATENCY, ACCURACY, COMPLETENESS, COHERENCE, RELEVANCE, COST, TOKEN_EFFICIENCY, CUSTOM |
| `__init__.py` | `TestCase` | Defines a benchmark test with prompt, expected outputs, forbidden outputs, tags, and optional latency constraints; `check_output()` validates agent responses |
| `__init__.py` | `EvalResult` | Captures a single evaluation run: agent ID, pass/fail, score, latency, token counts, cost, and errors |
| `__init__.py` | `BenchmarkResult` | Aggregated results per agent: pass rate, percentile latencies (p50/p95/p99), total cost, and per-tag breakdowns |
| `__init__.py` | `Scorer` | Abstract base class for scoring strategies; subclasses implement `score(output, expected) -> float` |
| `__init__.py` | `ExactMatchScorer` | Scores 1.0 on exact string match, 0.0 otherwise; optional case sensitivity |
| `__init__.py` | `ContainsScorer` | Scores 1.0 if expected text is a substring of output; default scorer used by `AgentBenchmark` |
| `__init__.py` | `LengthScorer` | Scores based on output length proximity to a target length with configurable tolerance |
| `__init__.py` | `CompositeScorer` | Combines multiple scorers with normalized weights |
| `__init__.py` | `AgentBenchmark[T]` | Generic benchmark runner: accepts agents and an executor callable, runs all test cases, aggregates results, and produces comparison reports or JSON exports |
| `__init__.py` | `create_basic_test_suite()` | Factory returning 5 pre-built `TestCase` instances covering greeting, math, JSON formatting, safety refusal, and coding |

## Operating Contracts

- `AgentBenchmark` is generic over agent type `T`; agents are decoupled from the benchmark via the `executor: Callable[[T, str], str]` parameter.
- `Scorer.score()` must return a float in the range `[0.0, 1.0]`.
- `TestCase.check_output()` performs case-insensitive substring matching for both `expected_contains` and `expected_not_contains`.
- `_run_test_case` catches `ValueError`, `RuntimeError`, `AttributeError`, `OSError`, and `TypeError`; other exceptions propagate.
- All errors are recorded in `EvalResult.errors` and aggregated into `BenchmarkResult.errors`.

## Integration Points

- **Depends on**: Standard library only (`json`, `statistics`, `time`, `abc`, `dataclasses`, `datetime`, `enum`)
- **Used by**: Agent comparison workflows, CI quality gates, and PAI VERIFY phase for agent performance validation

## Navigation

- **Parent**: [agents](../README.md)
- **Root**: [Codomyrmex](../../../../README.md)
