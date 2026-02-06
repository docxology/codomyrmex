# Chaos Engineering Module

Fault injection and resilience testing for system hardening.

## Quick Start

```python
from codomyrmex.chaos_engineering import (
    FaultInjector, FaultConfig, FaultType,
    ChaosExperiment, SteadyStateHypothesis,
)

# Inject latency
injector = FaultInjector()
injector.register_fault("api", FaultConfig(
    fault_type=FaultType.LATENCY,
    probability=0.3,
    duration_seconds=2.0,
))

# Run experiment
exp = ChaosExperiment(
    name="api-latency-test",
    hypothesis=SteadyStateHypothesis("api-responsive", check_api),
    action=lambda: injector.inject("api"),
)
result = exp.run()
```

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
