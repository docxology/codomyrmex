# Chaos Engineering — Functional Specification

**Module**: `codomyrmex.chaos_engineering`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Fault injection and resilience testing.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `FaultType` | Class | Types of injectable faults. |
| `FaultConfig` | Class | Configuration for a fault. |
| `FaultInjector` | Class | Inject faults into system components. |
| `InjectedFaultError` | Class | Raised when a fault is injected. |
| `SteadyStateHypothesis` | Class | Define expected steady state. |
| `ExperimentResult` | Class | Result of a chaos experiment. |
| `ChaosExperiment` | Class | A chaos engineering experiment. |
| `ChaosMonkey` | Class | Automated chaos testing. |
| `with_chaos()` | Function | Decorator to inject chaos into a function. |
| `register_fault()` | Function | Register a fault. |
| `remove_fault()` | Function | Remove a fault. |
| `should_inject()` | Function | Check if fault should be injected. |
| `inject()` | Function | Inject the fault (call after should_inject). |

### Source Files

- `scenarios.py`

## 3. Dependencies

See `src/codomyrmex/chaos_engineering/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.chaos_engineering import FaultType, FaultConfig, FaultInjector, InjectedFaultError, SteadyStateHypothesis
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k chaos_engineering -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/chaos_engineering/)
