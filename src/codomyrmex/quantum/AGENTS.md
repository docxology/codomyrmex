# Agent Guidelines - Quantum

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Quantum computing simulation with gates, circuits, and algorithms.

## Key Classes

- **QuantumCircuit** — Build quantum circuits (fluent API)
- **Gate** — Gate dataclass (gate_type, target, control, parameter)
- **GateType** — Enum of supported gate types
- **QuantumSimulator** — Statevector simulation
- **bell_state()** — Create Bell pair circuit
- **ghz_state(n)** — Create GHZ state circuit
- **circuit_to_ascii()** — Render circuit as ASCII art
- **circuit_stats()** — Get circuit statistics dict

## Agent Instructions

1. **Initialize qubits** — Start with |0⟩ state
2. **Apply gates in order** — Gates compose left-to-right
3. **Measure at end** — Measurement collapses state
4. **Use named states** — Bell, GHZ for entanglement
5. **Simulate before run** — Test on simulator first

## Common Patterns

```python
from codomyrmex.quantum import (
    QuantumCircuit, QuantumSimulator, bell_state, ghz_state,
    circuit_to_ascii, circuit_stats
)

# Build simple circuit (fluent API)
circuit = QuantumCircuit(2)
circuit.h(0).cnot(0, 1).measure_all()

# Simulate — returns dict[str, int] of bitstring counts
sim = QuantumSimulator()
counts = sim.run(circuit, shots=1000)
print(counts)  # {"00": ~500, "11": ~500}

# Create entangled states
bell = bell_state()
ghz = ghz_state(3)  # 3-qubit GHZ

# Visualize
print(circuit_to_ascii(bell))
# q0: -H--*--M-
# q1: ----X--M-

# Statistics
stats = circuit_stats(bell)
print(stats)  # {"num_qubits": 2, "num_gates": 2, ...}
```

## Testing Patterns

```python
# Verify Bell state
sim = QuantumSimulator()
counts = sim.run(bell_state(), shots=1000)
# Should produce only "00" and "11" outcomes
assert set(counts.keys()) <= {"00", "11"}
assert counts.get("00", 0) > 0
assert counts.get("11", 0) > 0
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Implements quantum algorithms and circuit simulations using `QuantumCircuit`, `QuantumSimulator`, and gate operations. Builds circuits with the fluent API, runs statevector simulations, and creates entangled states (Bell, GHZ).

### Architect Agent
**Use Cases**: Designs quantum-classical hybrid architectures, reviews circuit composition patterns, evaluates gate set completeness, and plans integration with classical optimization loops.

### QATester Agent
**Use Cases**: Validates quantum gate operations, verifies entanglement outcomes (Bell state produces only "00"/"11"), confirms circuit statistics accuracy, and tests simulator determinism with seeded runs.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
