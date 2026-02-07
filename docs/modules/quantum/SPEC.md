# Quantum — Functional Specification

**Module**: `codomyrmex.quantum`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Quantum algorithm primitives, simulation, and circuit patterns.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `GateType` | Class | Quantum gate types. |
| `Gate` | Class | A quantum gate. |
| `Qubit` | Class | A quantum bit state. |
| `QuantumCircuit` | Class | A quantum circuit. |
| `QuantumSimulator` | Class | Simple statevector quantum simulator. |
| `bell_state()` | Function | Create Bell state circuit. |
| `ghz_state()` | Function | Create GHZ state circuit. |
| `qft()` | Function | Quantum Fourier Transform circuit. |
| `zero()` | Function | zero |
| `one()` | Function | one |

## 3. Dependencies

See `src/codomyrmex/quantum/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.quantum import GateType, Gate, Qubit, QuantumCircuit, QuantumSimulator
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k quantum -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/quantum/)
