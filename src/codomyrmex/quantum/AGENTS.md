# Agent Guidelines - Quantum

## Module Overview

Quantum computing simulation with gates, circuits, and algorithms.

## Key Classes

- **QuantumCircuit** — Build quantum circuits
- **QuantumGate** — Quantum gate operations
- **QuantumSimulator** — Statevector simulation
- **create_bell_state()** — Create Bell pair
- **create_ghz_state(n)** — Create GHZ state

## Agent Instructions

1. **Initialize qubits** — Start with |0⟩ state
2. **Apply gates in order** — Gates compose left-to-right
3. **Measure at end** — Measurement collapses state
4. **Use named states** — Bell, GHZ for entanglement
5. **Simulate before run** — Test on simulator first

## Common Patterns

```python
from codomyrmex.quantum import (
    QuantumCircuit, QuantumSimulator, create_bell_state, create_ghz_state
)

# Build simple circuit
circuit = QuantumCircuit(2)
circuit.h(0)       # Hadamard on qubit 0
circuit.cx(0, 1)   # CNOT: control=0, target=1

# Simulate
sim = QuantumSimulator()
result = sim.run(circuit)
print(f"Statevector: {result.statevector}")
print(f"Probabilities: {result.probabilities}")

# Create entangled states
bell = create_bell_state()
ghz = create_ghz_state(3)  # 3-qubit GHZ
```

## Testing Patterns

```python
# Verify Bell state
bell = create_bell_state()
sim = QuantumSimulator()
result = sim.run(bell)
# Should have 50% |00⟩ and 50% |11⟩
assert abs(result.probabilities[0] - 0.5) < 0.01
assert abs(result.probabilities[3] - 0.5) < 0.01
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
