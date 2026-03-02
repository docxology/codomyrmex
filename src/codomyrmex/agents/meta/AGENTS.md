# Codomyrmex Agents — src/codomyrmex/agents/meta

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Self-improving meta-agent framework that wraps task execution, scores outcomes across multiple dimensions (correctness, efficiency, quality, speed), and evolves strategy selection over time using A/B testing and success-rate tracking.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `meta_agent.py` | `MetaAgent` | Orchestrates the learning loop: select strategy, execute task, score outcome, update success rate |
| `meta_agent.py` | `EvolutionRecord` | Dataclass capturing iteration number, strategy used, and composite score |
| `ab_testing.py` | `ABTestEngine` | Compares two strategies over paired score lists using binomial proportion test |
| `ab_testing.py` | `ABTestResult` | Dataclass with wins_a, wins_b, ties, winner, and statistical significance |
| `scoring.py` | `OutcomeScorer` | Computes weighted composite from correctness, efficiency, quality, and speed |
| `scoring.py` | `OutcomeScore` | Dataclass holding the four dimension scores plus composite |
| `strategies.py` | `StrategyLibrary` | CRUD operations on named strategies; tracks success rates and selects best |
| `strategies.py` | `Strategy` | Named strategy with prompt template, parameters, running success rate |

## Operating Contracts

- `MetaAgent.run()` selects the best strategy (or round-robins) each iteration, calls `task_fn(strategy.name)`, and updates `Strategy.success_rate` based on a composite > 0.5 threshold.
- `OutcomeScorer` default weights: correctness 0.4, quality 0.25, efficiency 0.2, speed 0.15. Custom weights accepted via constructor.
- `ABTestEngine.compare_scores()` uses a simple binomial proportion approximation: `significance = abs(p_a - 0.5) * 2` where `p_a` is the win fraction.
- `Strategy.record_outcome()` uses a running weighted average: `success_rate = success_rate * (1 - 1/count) + outcome * (1/count)`.
- Errors in `task_fn` are caught, logged, and counted as failures (score 0.0) rather than aborting the loop.
- All components log via `logging_monitoring.get_logger()` before re-raising or returning.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring`
- **Used by**: Agent orchestration workflows, PAI meta-learning loops

## Navigation

- **Parent**: [agents](../README.md)
- **Root**: [Root](../../../../README.md)
