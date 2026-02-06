# Quantum Computing Module

Quantum algorithm primitives, simulation, and circuit patterns.

```python
from codomyrmex.quantum import (
    QuantumCircuit, QuantumSimulator,
    bell_state, ghz_state,
)

# Create Bell state
circuit = bell_state()
sim = QuantumSimulator()
results = sim.run(circuit, shots=1000)
print(results)  # {'00': ~500, '11': ~500}
```
