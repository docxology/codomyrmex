# Personal AI Infrastructure — Quantum Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Quantum module provides PAI integration for quantum computing simulation, enabling AI agents to experiment with quantum algorithms.

## PAI Capabilities

### Quantum Circuit Building

Build quantum circuits with a fluent API:

```python
from codomyrmex.quantum import QuantumCircuit, QuantumSimulator

# Create Bell state circuit
circuit = QuantumCircuit(2)
circuit.h(0).cnot(0, 1).measure_all()

# Simulate — returns dict[str, int] of bitstring -> count
sim = QuantumSimulator()
counts = sim.run(circuit, shots=1000)
print(counts)  # {"00": ~500, "11": ~500}
```

### Quantum Algorithm Exploration

Use built-in algorithm functions and visualization:

```python
from codomyrmex.quantum import (
    qft, bell_state, ghz_state,
    circuit_to_ascii, circuit_stats
)

# Quantum Fourier Transform
qft_circuit = qft(4)

# Analyze circuit with circuit_stats()
stats = circuit_stats(qft_circuit)
print(f"Depth: {stats['depth']}")
print(f"Gates: {stats['num_gates']}")
print(f"Gate breakdown: {stats['gate_counts']}")

# Visualize as ASCII
print(circuit_to_ascii(bell_state()))
# q0: -H--*--M-
# q1: ----X--M-
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `QuantumCircuit` | Build quantum programs (fluent API) |
| `QuantumSimulator` | Test quantum algorithms |
| `Gate` / `GateType` | Gate representation |
| `circuit_to_ascii` | Visualize circuits |
| `circuit_stats` | Analyze circuit complexity |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
