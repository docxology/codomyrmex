# Quantum Computing Module

**Version**: v0.1.0 | **Status**: Active

Quantum algorithm primitives, circuit simulation, and gate operations.

## Quick Start

```python
from codomyrmex.quantum import QuantumCircuit, QuantumSimulator, bell_state

# Create and run Bell state
circuit = bell_state()
simulator = QuantumSimulator()
counts = simulator.run(circuit, shots=1000)
print(counts)  # {'00': ~500, '11': ~500}

# Build custom circuit
qc = QuantumCircuit(2)
qc.h(0)           # Hadamard on qubit 0
qc.cnot(0, 1)     # CNOT: control=0, target=1
qc.measure_all()

results = simulator.run(qc, shots=1024)
```

## Exports

| Class/Function | Description |
|----------------|-------------|
| `QuantumCircuit` | Build circuits with h, x, y, z, cnot, rx, ry, rz gates |
| `QuantumSimulator` | Statevector simulator with measurement |
| `Gate` | Single gate with type, target, control, parameter |
| `GateType` | Enum: H, X, Y, Z, CNOT, CZ, RX, RY, RZ, T, S, SWAP |
| `Qubit` | Qubit state with alpha/beta amplitudes |
| `bell_state()` | Pre-built Bell state circuit |
| `ghz_state(n)` | GHZ entanglement for n qubits |
| `qft(n)` | Quantum Fourier Transform circuit |

## Supported Gates

| Gate | Method | Description |
|------|--------|-------------|
| Hadamard | `.h(q)` | Superposition |
| Pauli-X | `.x(q)` | NOT / bit flip |
| Pauli-Y | `.y(q)` | Y rotation |
| Pauli-Z | `.z(q)` | Phase flip |
| CNOT | `.cnot(c, t)` | Controlled-NOT |
| CZ | `.cz(c, t)` | Controlled-Z |
| RX | `.rx(q, θ)` | X-axis rotation |
| RY | `.ry(q, θ)` | Y-axis rotation |
| RZ | `.rz(q, θ)` | Z-axis rotation |

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
