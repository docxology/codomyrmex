# Chaos Engineering Module

**Version**: v0.1.0 | **Status**: Active

Fault injection and resilience testing.


## Installation

```bash
uv pip install codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes
- **`FaultType`** — Types of injectable faults.
- **`FaultConfig`** — Configuration for a fault.
- **`FaultInjector`** — Inject faults into system components.
- **`InjectedFaultError`** — Raised when a fault is injected.
- **`SteadyStateHypothesis`** — Define expected steady state.
- **`ExperimentResult`** — Result of a chaos experiment.
- **`ChaosExperiment`** — A chaos engineering experiment.
- **`ChaosMonkey`** — Automated chaos testing.

### Functions
- **`with_chaos()`** — Decorator to inject chaos into a function.

## Quick Start

```python
from codomyrmex.chaos_engineering import (
    FaultInjector, FaultType, FaultConfig,
    ChaosExperiment, ChaosMonkey, SteadyStateHypothesis
)

# Inject faults
injector = FaultInjector()
injector.register_fault("db-slow", FaultConfig(
    fault_type=FaultType.LATENCY,
    probability=0.3,  # 30% of calls
    duration_seconds=2.0
))

# Use in code
injector.maybe_inject("db-slow")  # Probabilistically adds 2s delay

# Define a chaos experiment
hypothesis = SteadyStateHypothesis(
    name="Service responds under 500ms",
    check_fn=lambda: check_response_time() < 0.5
)

experiment = ChaosExperiment(
    name="Database Latency Test",
    hypothesis=hypothesis,
    action=lambda: injector.inject("db-slow"),
    rollback=lambda: injector.remove_fault("db-slow")
)

result = experiment.run()
print(f"Passed: {result.success}, Duration: {result.duration_seconds:.2f}s")
```

## ChaosMonkey

```python
# Automated chaos testing
monkey = ChaosMonkey()
monkey.add_experiment(experiment)

# Run all experiments
results = monkey.run_all()

# Run random experiment
result = monkey.run_random()
```

## Exports

| Class | Description |
|-------|-------------|
| `FaultInjector` | Register and trigger faults |
| `FaultType` | Enum: latency, error, timeout, resource_exhaustion, network_partition |
| `FaultConfig` | Fault settings: type, probability, duration |
| `ChaosExperiment` | Define hypothesis, action, rollback |
| `ChaosMonkey` | Run experiments automatically |
| `SteadyStateHypothesis` | Expected system behavior |
| `ExperimentResult` | Experiment outcome with timing |
| `InjectedFaultError` | Error raised by fault injection |
| `with_chaos` | Decorator for chaos-protected functions |


## Documentation

- [Module Documentation](../../../docs/modules/chaos_engineering/README.md)
- [Agent Guide](../../../docs/modules/chaos_engineering/AGENTS.md)
- [Specification](../../../docs/modules/chaos_engineering/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
