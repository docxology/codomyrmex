# Meta — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Self-improving meta-agent subsystem that tracks agent task outcomes across four dimensions and evolves strategy selection using success-rate tracking and A/B testing. Designed as a pluggable wrapper around any task function.

## Architecture

The meta system uses a Strategy Pattern with feedback:

1. `StrategyLibrary` stores named strategies with prompt templates and running success rates
2. `MetaAgent.run()` iterates: select best strategy -> execute task -> score outcome -> update success rate
3. `OutcomeScorer` produces a weighted composite score from four independent dimensions
4. `ABTestEngine` provides pairwise strategy comparison for offline evaluation

## Key Classes

### `MetaAgent`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `library: StrategyLibrary`, `scorer: OutcomeScorer`, `ab_engine: ABTestEngine` | `None` | Initialize with optional custom components |
| `run` | `task_fn: Callable[[str], dict]`, `iterations: int = 5` | `list[EvolutionRecord]` | Execute the learning loop for N iterations |
| `history` | (property) | `list[EvolutionRecord]` | Immutable copy of evolution history |
| `improvement` | (property) | `float` | Score delta between first and last iteration |

### `OutcomeScorer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `weights: dict[str, float]` | `None` | Custom dimension weights (default: correctness=0.4, efficiency=0.2, quality=0.25, speed=0.15) |
| `score` | `tests_passed`, `tests_total`, `tokens_used`, `token_budget`, `quality_issues`, `max_quality_issues`, `elapsed_seconds`, `time_budget` | `OutcomeScore` | Compute multi-dimensional score |

### `ABTestEngine`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `compare_scores` | `name_a: str`, `scores_a: list[float]`, `name_b: str`, `scores_b: list[float]` | `ABTestResult` | Pairwise comparison with significance estimate |

### `StrategyLibrary`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add` | `strategy: Strategy` | `None` | Register a strategy |
| `get` | `name: str` | `Strategy or None` | Lookup by name |
| `remove` | `name: str` | `bool` | Remove by name |
| `list_strategies` | — | `list[Strategy]` | All strategies sorted by success rate (descending) |
| `best_strategy` | — | `Strategy or None` | Highest success-rate strategy |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring`
- **External**: Standard library only (`dataclasses`, `collections.abc`, `typing`)

## Constraints

- Composite score is clamped to [0.0, 1.0].
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.
- `task_fn` exceptions are caught and logged, not propagated.

## Error Handling

- `MetaAgent.run()` catches all exceptions from `task_fn`, logs via `logger.warning`, records outcome as failure.
- `OutcomeScorer.score()` uses `max()` guards to prevent division by zero on all dimension calculations.
