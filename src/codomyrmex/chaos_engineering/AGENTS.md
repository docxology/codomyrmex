# Agent Guidelines - Chaos Engineering

## Module Overview

Controlled failure injection for resilience testing.

## Key Classes

- **FaultInjector** — Inject faults
- **ChaosExperiment** — Define experiments
- **ChaosMonkey** — Random fault injection
- **SteadyStateHypothesis** — Define normal state

## Agent Instructions

1. **Start small** — Controlled experiments first
2. **Define steady state** — Know what "normal" looks like
3. **Blast radius** — Limit impact scope
4. **Rollback ready** — Abort if needed
5. **Learn from failures** — Document findings

## Common Patterns

```python
from codomyrmex.chaos_engineering import (
    ChaosExperiment, FaultInjector, FaultType, with_chaos
)

# Define experiment
experiment = ChaosExperiment(
    name="database_failure",
    steady_state={"response_time": "<500ms", "error_rate": "<1%"},
    blast_radius=["service-a"],
    duration=60
)

# Inject faults
injector = FaultInjector()
injector.inject(FaultType.LATENCY, target="db", delay_ms=1000)
injector.inject(FaultType.FAILURE, target="cache", probability=0.1)

# Run experiment
result = experiment.run()
print(f"Hypothesis held: {result.hypothesis_held}")

# Decorator for chaos
@with_chaos(probability=0.01, fault=FaultType.LATENCY)
def api_handler():
    return process_request()
```

## Testing Patterns

```python
# Verify fault injection
injector = FaultInjector()
injector.inject(FaultType.LATENCY, delay_ms=100)
assert injector.is_active

# Verify experiment
exp = ChaosExperiment("test")
result = exp.run(dry_run=True)
assert result.dry_run
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
