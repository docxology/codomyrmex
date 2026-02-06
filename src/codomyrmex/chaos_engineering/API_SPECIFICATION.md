# Chaos Engineering API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## 1. Overview

The `chaos_engineering` module provides fault injection and resilience testing capabilities. It implements the chaos engineering discipline: define steady state, inject faults, observe whether the system maintains its invariants, and roll back.

## 2. Core Components

### 2.1 Enums

- **`FaultType`**: Types of injectable faults -- `LATENCY`, `ERROR`, `TIMEOUT`, `RESOURCE_EXHAUSTION`, `NETWORK_PARTITION`.

### 2.2 Configuration

**`FaultConfig`** (dataclass): Defines a single fault.
- `fault_type: FaultType` -- The type of fault to inject.
- `probability: float = 0.1` -- Injection probability (0.0 to 1.0).
- `duration_seconds: float = 0.0` -- Duration for latency/timeout faults.
- `error_message: str = "Injected fault"` -- Message for error-type faults.
- `metadata: dict[str, Any]` -- Arbitrary configuration data.

### 2.3 Fault Injector

```python
from codomyrmex.chaos_engineering import FaultInjector, FaultConfig, FaultType

injector = FaultInjector()

# Register a fault
config = FaultConfig(fault_type=FaultType.LATENCY, probability=0.3, duration_seconds=2.0)
injector.register_fault("slow-database", config)

# Check and inject
if injector.should_inject("slow-database"):  # -> bool (probabilistic)
    injector.inject("slow-database")          # Sleeps 2s for LATENCY type

# Combined check + inject
injector.maybe_inject("slow-database")

# Remove fault
injector.remove_fault("slow-database")  # -> bool
```

**Injection behavior by FaultType:**
| FaultType | Behavior |
|:----------|:---------|
| `LATENCY` | `time.sleep(duration_seconds)` |
| `ERROR` | Raises `InjectedFaultError(error_message)` |
| `TIMEOUT` | Sleeps then raises `TimeoutError(error_message)` |
| `RESOURCE_EXHAUSTION` | Defined via metadata (extensible) |
| `NETWORK_PARTITION` | Defined via metadata (extensible) |

### 2.4 Chaos Experiments

**`SteadyStateHypothesis`** (dataclass): Defines the expected normal state.
- `name: str` -- Hypothesis name.
- `check_fn: Callable[[], bool]` -- Returns `True` if system is in steady state.
- `description: str` -- Human-readable description.

**`ExperimentResult`** (dataclass): Outcome of an experiment run.
- `experiment_name`, `success`, `steady_state_before`, `steady_state_after`, `duration_seconds`, `error`, `started_at`.

```python
from codomyrmex.chaos_engineering import (
    ChaosExperiment, SteadyStateHypothesis, ExperimentResult
)

hypothesis = SteadyStateHypothesis(
    name="api-responds",
    check_fn=lambda: health_check() == 200,
    description="API returns 200 on health endpoint",
)

experiment = ChaosExperiment(
    name="kill-cache",
    hypothesis=hypothesis,
    action=lambda: stop_redis(),
    rollback=lambda: start_redis(),
)

result: ExperimentResult = experiment.run()
# result.success == True means system maintained steady state
```

### 2.5 Chaos Monkey

```python
from codomyrmex.chaos_engineering import ChaosMonkey

monkey = ChaosMonkey(injector=injector)
monkey.add_experiment(experiment)

results = monkey.run_all()       # Run all experiments sequentially
result = monkey.run_random()     # Run one random experiment
history = monkey.results          # All past results
```

### 2.6 Decorator

```python
from codomyrmex.chaos_engineering import with_chaos, FaultInjector

injector = FaultInjector()
injector.register_fault("flaky-api", FaultConfig(fault_type=FaultType.ERROR, probability=0.1))

@with_chaos(injector, "flaky-api")
def call_external_api():
    ...
```

## 3. Error Handling

| Exception | Raised When |
|:----------|:------------|
| `InjectedFaultError` | Fault of type `ERROR` is injected |
| `TimeoutError` (builtin) | Fault of type `TIMEOUT` is injected |

`ChaosExperiment.run()` catches all exceptions during action execution and reports them in `ExperimentResult.error`. Rollback failures are appended to the error string.

## 4. Thread Safety

`FaultInjector` is thread-safe via `threading.Lock`. Experiment execution is synchronous and single-threaded.

## 5. Integration Points

- **service_mesh**: Test circuit breaker behavior under fault conditions.
- **metrics**: Track experiment success rates and fault injection frequency.
- **logging_monitoring**: Log experiment results and fault injection events.

## 6. Navigation

- **Human Documentation**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent Directory**: [codomyrmex](../README.md)
