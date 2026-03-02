# Chaos Engineering -- Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Chaos engineering module providing fault injection, experiment orchestration, and pre-built failure scenario simulation. Implements the steady-state hypothesis pattern for resilience validation.

## Architecture

```
chaos/
  __init__.py    -- FaultInjector, ChaosExperiment, ChaosMonkey, with_chaos decorator, data classes
  scenarios.py   -- ChaosScenarioRunner (async), GameDay, ScenarioType/Config/Result
```

## Key Classes

### FaultInjector

Thread-safe fault registry supporting probabilistic injection.

| Method | Signature | Description |
|--------|-----------|-------------|
| `register_fault` | `(name: str, config: FaultConfig) -> None` | Register a named fault |
| `remove_fault` | `(name: str) -> bool` | Remove fault, returns success |
| `should_inject` | `(name: str) -> bool` | Probabilistic check against `FaultConfig.probability` |
| `inject` | `(name: str) -> None` | Execute fault: LATENCY sleeps, ERROR raises `InjectedFaultError`, TIMEOUT sleeps then raises `TimeoutError` |
| `maybe_inject` | `(name: str) -> None` | Combined `should_inject` + `inject` |

### FaultType (Enum)

Values: `LATENCY`, `ERROR`, `TIMEOUT`, `RESOURCE_EXHAUSTION`, `NETWORK_PARTITION`

### FaultConfig (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `fault_type` | `FaultType` | required | Type of fault to inject |
| `probability` | `float` | `0.1` | Injection probability (0.0--1.0) |
| `duration_seconds` | `float` | `0.0` | Duration for LATENCY/TIMEOUT faults |
| `error_message` | `str` | `"Injected fault"` | Message for raised exceptions |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

### ChaosExperiment

| Method | Signature | Description |
|--------|-----------|-------------|
| `run` | `() -> ExperimentResult` | Verify steady state, execute action, verify again, rollback if provided |

Constructor: `(name, hypothesis: SteadyStateHypothesis, action: Callable, rollback: Callable | None)`

### ChaosMonkey

| Method | Signature | Description |
|--------|-----------|-------------|
| `add_experiment` | `(experiment: ChaosExperiment) -> None` | Register experiment |
| `run_all` | `() -> list[ExperimentResult]` | Run all experiments sequentially |
| `run_random` | `() -> ExperimentResult | None` | Run one random experiment |

### ChaosScenarioRunner (async)

| Method | Signature | Description |
|--------|-----------|-------------|
| `run` | `async (config: ScenarioConfig) -> ScenarioResult` | Run scenario by type |

Implements 4 of 8 `ScenarioType` values: `NETWORK_PARTITION`, `SERVICE_OUTAGE`, `HIGH_LATENCY`, `CASCADING_FAILURE`.

### GameDay

| Method | Signature | Description |
|--------|-----------|-------------|
| `add_scenario` | `(config: ScenarioConfig) -> GameDay` | Fluent scenario registration |
| `run_all` | `async (parallel: bool = False) -> list[ScenarioResult]` | Run all scenarios; parallel uses `asyncio.gather` |
| `report` | `() -> str` | Generate markdown report with pass/fail summary |

## Dependencies

- Standard library: `random`, `threading`, `time`, `asyncio`
- Optional: `codomyrmex.validation.schemas` (Result, ResultStatus)

## Constraints

- `FaultInjector` only implements behavior for LATENCY, ERROR, and TIMEOUT fault types. RESOURCE_EXHAUSTION and NETWORK_PARTITION are defined but not directly handled by `inject()`.
- `ChaosScenarioRunner` implements 4 of 8 scenario types. Unknown types return a failing `ScenarioResult`.
- `with_chaos` decorator calls `maybe_inject` before the wrapped function, not after.

## Error Handling

- `InjectedFaultError(Exception)`: Raised by `FaultInjector.inject()` for ERROR fault type
- `ChaosExperiment.run()` catches all exceptions during action, steady-state checks, and rollback; aggregates errors in `ExperimentResult.error`
- `ChaosScenarioRunner.run()` returns a failing result for unregistered scenario types rather than raising
