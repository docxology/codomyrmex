# Chaos Engineering Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Fault injection and resilience testing.

## Key Features

- **FaultType** — Types of injectable faults.
- **FaultConfig** — Configuration for a fault.
- **FaultInjector** — Inject faults into system components.
- **InjectedFaultError** — Raised when a fault is injected.
- **SteadyStateHypothesis** — Define expected steady state.
- **ExperimentResult** — Result of a chaos experiment.
- `with_chaos()` — Decorator to inject chaos into a function.
- `register_fault()` — Register a fault.
- `remove_fault()` — Remove a fault.
- `should_inject()` — Check if fault should be injected.

## Quick Start

```python
from codomyrmex.chaos_engineering import FaultType, FaultConfig, FaultInjector

# Initialize
instance = FaultType()
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `FaultType` | Types of injectable faults. |
| `FaultConfig` | Configuration for a fault. |
| `FaultInjector` | Inject faults into system components. |
| `InjectedFaultError` | Raised when a fault is injected. |
| `SteadyStateHypothesis` | Define expected steady state. |
| `ExperimentResult` | Result of a chaos experiment. |
| `ChaosExperiment` | A chaos engineering experiment. |
| `ChaosMonkey` | Automated chaos testing. |

### Functions

| Function | Description |
|----------|-------------|
| `with_chaos()` | Decorator to inject chaos into a function. |
| `register_fault()` | Register a fault. |
| `remove_fault()` | Remove a fault. |
| `should_inject()` | Check if fault should be injected. |
| `inject()` | Inject the fault (call after should_inject). |
| `maybe_inject()` | Inject fault probabilistically. |
| `run()` | Run the experiment. |
| `add_experiment()` | Add an experiment. |
| `run_all()` | Run all experiments. |
| `run_random()` | Run a random experiment. |
| `results()` | results |
| `decorator()` | decorator |
| `wrapper()` | wrapper |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/chaos_engineering/](../../../src/codomyrmex/chaos_engineering/)
- **Parent**: [Modules](../README.md)
