# Quantum Module — Agent Coordination

## Purpose

Quantum algorithm primitives, simulation, and circuit patterns.

## Key Capabilities

- **GateType**: Quantum gate types.
- **Gate**: A quantum gate.
- **Qubit**: A quantum bit state.
- **QuantumCircuit**: A quantum circuit.
- **QuantumSimulator**: Simple statevector quantum simulator.
- `bell_state()`: Create Bell state circuit.
- `ghz_state()`: Create GHZ state circuit.
- `qft()`: Quantum Fourier Transform circuit.

## Agent Usage Patterns

```python
from codomyrmex.quantum import GateType

# Agent initializes quantum
instance = GateType()
```

## Integration Points

- **Source**: [src/codomyrmex/quantum/](../../../src/codomyrmex/quantum/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k quantum -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
