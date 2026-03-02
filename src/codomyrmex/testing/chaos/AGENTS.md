# Chaos Engineering -- Agentic Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides fault injection and resilience testing primitives for verifying system behavior under failure conditions. Agents use this module to simulate latency, errors, timeouts, resource exhaustion, and network partitions.

## Key Components

| Component | Source | Role |
|-----------|--------|------|
| `FaultInjector` | `__init__.py` | Thread-safe fault registry with probabilistic injection via `register_fault()`, `should_inject()`, `inject()`, `maybe_inject()` |
| `ChaosExperiment` | `__init__.py` | Structured experiment runner: verifies steady state before/after action, with optional rollback |
| `ChaosMonkey` | `__init__.py` | Orchestrates multiple experiments via `run_all()` or `run_random()` |
| `ChaosScenarioRunner` | `scenarios.py` | Async runner with 4 built-in scenarios: network partition, service outage, high latency, cascading failure |
| `GameDay` | `scenarios.py` | Coordinated multi-scenario runner with sequential or parallel execution and markdown report generation |
| `with_chaos` | `__init__.py` | Decorator for probabilistic fault injection on any function |

## Operating Contracts

1. **Fault Registration**: Register faults via `FaultInjector.register_fault(name, FaultConfig)` before injection. `FaultConfig.probability` controls injection rate (0.0--1.0).
2. **Steady State**: Every `ChaosExperiment` requires a `SteadyStateHypothesis` with a `check_fn` returning `bool`. Experiment fails if system is not in steady state before the action.
3. **Rollback**: `ChaosExperiment` accepts an optional `rollback` callable invoked after the action regardless of outcome.
4. **Scenario Types**: `ScenarioType` enum defines 8 failure modes; `ChaosScenarioRunner` implements 4 (NETWORK_PARTITION, SERVICE_OUTAGE, HIGH_LATENCY, CASCADING_FAILURE).
5. **Thread Safety**: `FaultInjector` uses `threading.Lock` for concurrent access to the active faults registry.

## Integration Points

- **validation.schemas**: Optional import of `Result` and `ResultStatus` for cross-module interop
- **testing parent**: Part of the `testing` module alongside `fixtures`, `generators`, and `workflow`
- **CLI**: `cli_commands()` exposes `experiments` and `run` subcommands

## Navigation

- **Parent**: [testing/](../README.md)
- **Siblings**: [fixtures/](../fixtures/), [generators/](../generators/), [workflow/](../workflow/)
- **Spec**: [SPEC.md](SPEC.md)
