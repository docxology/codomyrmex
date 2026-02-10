# Quantum - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Quantum computing simulation module providing quantum gates, circuits, and algorithm implementations.

## Functional Requirements

- Quantum circuit construction and manipulation
- Single and multi-qubit gate operations
- Statevector simulation
- Measurement and probability calculation
- Common quantum state preparation (Bell, GHZ, QFT)

## Core Classes

| Class | Description |
|-------|-------------|
| `QuantumCircuit` | Quantum circuit builder (fluent API) |
| `Gate` | Gate dataclass (gate_type, target, control, parameter) |
| `GateType` | Enum of supported gate types |
| `QuantumSimulator` | Statevector simulator |
| `Qubit` | Qubit state representation |

## Key Functions

| Function | Description |
|----------|-------------|
| `bell_state()` | Create 2-qubit Bell pair circuit |
| `ghz_state(n)` | Create n-qubit GHZ state circuit |
| `qft(n)` | Create n-qubit QFT circuit |
| `circuit_to_ascii(circuit)` | Render circuit as ASCII art |
| `circuit_stats(circuit)` | Return circuit statistics dict |

## Supported Gates

- Single-qubit: H, X, Y, Z, S, T, Rx, Ry, Rz
- Multi-qubit: CNOT, CZ, SWAP

## Design Principles

1. **Mathematical Accuracy**: Precise complex number operations
2. **Educational**: Clear API for learning quantum computing
3. **Scalability**: Efficient simulation for moderate qubit counts

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k quantum -v
```
