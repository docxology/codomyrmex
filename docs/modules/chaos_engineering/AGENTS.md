# Chaos Engineering Module — Agent Coordination

## Purpose

Fault injection and resilience testing.

## Key Capabilities

- **FaultType**: Types of injectable faults.
- **FaultConfig**: Configuration for a fault.
- **FaultInjector**: Inject faults into system components.
- **InjectedFaultError**: Raised when a fault is injected.
- **SteadyStateHypothesis**: Define expected steady state.
- `with_chaos()`: Decorator to inject chaos into a function.
- `register_fault()`: Register a fault.
- `remove_fault()`: Remove a fault.

## Agent Usage Patterns

```python
from codomyrmex.chaos_engineering import FaultType

# Agent initializes chaos engineering
instance = FaultType()
```

## Integration Points

- **Source**: [src/codomyrmex/chaos_engineering/](../../../src/codomyrmex/chaos_engineering/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Key Components

- **`FaultType`** — Types of injectable faults.
- **`FaultConfig`** — Configuration for a fault.
- **`FaultInjector`** — Inject faults into system components.
- **`InjectedFaultError`** — Raised when a fault is injected.
- **`SteadyStateHypothesis`** — Define expected steady state.
- **`with_chaos()`** — Decorator to inject chaos into a function.

