# Personal AI Infrastructure — Chaos Engineering Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Chaos Engineering module provides PAI integration for resilience testing, enabling AI agents to proactively identify system weaknesses.

## PAI Capabilities

### Automated Resilience Testing

Run chaos experiments as part of CI/CD:

```python
from codomyrmex.chaos_engineering import (
    ChaosExperiment, FaultInjector, FaultType
)

# Define experiment
experiment = ChaosExperiment(
    name="database_latency_test",
    steady_state={"response_time": "<500ms"},
    duration=60
)

# Inject fault
injector = FaultInjector()
injector.inject(FaultType.LATENCY, target="db", delay_ms=200)

# Run and validate
result = experiment.run()
print(f"Hypothesis held: {result.hypothesis_held}")
```

### AI-Driven Chaos

Let AI agents discover weaknesses:

```python
from codomyrmex.chaos_engineering import ChaosMonkey

# Random fault injection
monkey = ChaosMonkey(
    targets=["api", "cache", "db"],
    probability=0.1
)

# Run with monitoring
monkey.start()
# ... observe system behavior ...
monkey.stop()
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `ChaosExperiment` | Automated resilience testing |
| `FaultInjector` | Controlled failure injection |
| `ChaosMonkey` | Discovery of unknown weaknesses |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
