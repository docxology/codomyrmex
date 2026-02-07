# Quantum Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Quantum algorithm primitives, simulation, and circuit patterns.

## Key Features

- **GateType** — Quantum gate types.
- **Gate** — A quantum gate.
- **Qubit** — A quantum bit state.
- **QuantumCircuit** — A quantum circuit.
- **QuantumSimulator** — Simple statevector quantum simulator.
- `bell_state()` — Create Bell state circuit.
- `ghz_state()` — Create GHZ state circuit.
- `qft()` — Quantum Fourier Transform circuit.
- `zero()` — zero

## Quick Start

```python
from codomyrmex.quantum import GateType, Gate, Qubit

# Initialize
instance = GateType()
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `GateType` | Quantum gate types. |
| `Gate` | A quantum gate. |
| `Qubit` | A quantum bit state. |
| `QuantumCircuit` | A quantum circuit. |
| `QuantumSimulator` | Simple statevector quantum simulator. |

### Functions

| Function | Description |
|----------|-------------|
| `bell_state()` | Create Bell state circuit. |
| `ghz_state()` | Create GHZ state circuit. |
| `qft()` | Quantum Fourier Transform circuit. |
| `zero()` | zero |
| `one()` | one |
| `plus()` | |+⟩ state. |
| `minus()` | |−⟩ state. |
| `prob_0()` | prob 0 |
| `prob_1()` | prob 1 |
| `measure()` | Measure qubit, collapsing state. |
| `h()` | Add Hadamard gate. |
| `x()` | Add Pauli-X gate. |
| `y()` | Add Pauli-Y gate. |
| `z()` | Add Pauli-Z gate. |
| `cnot()` | Add CNOT gate. |
| `cz()` | Add CZ gate. |
| `rx()` | Add RX rotation. |
| `ry()` | Add RY rotation. |
| `rz()` | Add RZ rotation. |
| `measure()` | Add measurement. |
| `measure_all()` | Measure all qubits. |
| `run()` | Run circuit and return measurement counts. |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/quantum/](../../../src/codomyrmex/quantum/)
- **Parent**: [Modules](../README.md)
