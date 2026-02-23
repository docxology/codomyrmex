# Quantum - API Specification

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Quantum module provides quantum circuit construction, statevector simulation, and common quantum algorithm primitives (Bell state, GHZ state, QFT). All simulation is classical -- no quantum hardware required.

## Enums

### `GateType`

Supported quantum gate types.

- `GateType.H` - Hadamard
- `GateType.X` - Pauli-X (NOT)
- `GateType.Y` - Pauli-Y
- `GateType.Z` - Pauli-Z
- `GateType.CNOT` - Controlled-NOT (two-qubit)
- `GateType.SWAP` - Swap (two-qubit)
- `GateType.T` - T gate (pi/4 phase)
- `GateType.S` - S gate (pi/2 phase)
- `GateType.RX` - Rotation around X-axis (parameterized)
- `GateType.RY` - Rotation around Y-axis (parameterized)
- `GateType.RZ` - Rotation around Z-axis (parameterized)
- `GateType.CZ` - Controlled-Z (two-qubit)

## Data Classes

### `Gate`

Represents a gate in a circuit.

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `gate_type` | `GateType` | required | The gate operation |
| `target` | `int` | required | Target qubit index |
| `control` | `int | None` | `None` | Control qubit for two-qubit gates |
| `parameter` | `float | None` | `None` | Rotation angle for RX/RY/RZ |

### `Qubit`

Represents a single qubit state as amplitudes.

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `alpha` | `complex` | `1+0j` | Amplitude of |0> |
| `beta` | `complex` | `0+0j` | Amplitude of |1> |

#### Class Methods

- `Qubit.zero() -> Qubit` - Returns |0> state.
- `Qubit.one() -> Qubit` - Returns |1> state.
- `Qubit.plus() -> Qubit` - Returns |+> state (equal superposition).
- `Qubit.minus() -> Qubit` - Returns |-> state.

#### Properties

- `prob_0 -> float` - Probability of measuring 0.
- `prob_1 -> float` - Probability of measuring 1.

#### `Qubit.measure() -> int`

- **Description**: Measure the qubit, collapsing state to |0> or |1>.
- **Returns**: `int` - `0` or `1` (probabilistic).

## Classes

### `QuantumCircuit`

Builder for quantum circuits with a fluent API.

#### `QuantumCircuit.__init__(num_qubits, num_classical_bits=0)`

- **Parameters**:
    - `num_qubits` (int): Number of qubits.
    - `num_classical_bits` (int): Number of classical bits. Defaults to `num_qubits`.

#### Gate Methods (all return `self` for chaining)

- `h(qubit) -> QuantumCircuit` - Add Hadamard gate.
- `x(qubit) -> QuantumCircuit` - Add Pauli-X gate.
- `y(qubit) -> QuantumCircuit` - Add Pauli-Y gate.
- `z(qubit) -> QuantumCircuit` - Add Pauli-Z gate.
- `cnot(control, target) -> QuantumCircuit` - Add CNOT gate.
- `swap(qubit1, qubit2) -> QuantumCircuit` - Add SWAP gate (two-qubit).
- `cz(control, target) -> QuantumCircuit` - Add Controlled-Z gate.
- `rx(qubit, theta) -> QuantumCircuit` - Add RX rotation (theta in radians).
- `ry(qubit, theta) -> QuantumCircuit` - Add RY rotation.
- `rz(qubit, theta) -> QuantumCircuit` - Add RZ rotation.

#### Measurement Methods

- `measure(qubit, classical_bit) -> QuantumCircuit` - Map qubit measurement to a classical bit.
- `measure_all() -> QuantumCircuit` - Measure all qubits to corresponding classical bits.

### `QuantumSimulator`

Statevector simulator. Executes circuits by applying gate matrices to a full state vector.

#### `QuantumSimulator.__init__()`

No parameters. State is initialized per-run.

#### `QuantumSimulator.run(circuit, shots=1024) -> dict[str, int]`

- **Description**: Simulate the circuit for a number of shots and return measurement counts.
- **Parameters**:
    - `circuit` (QuantumCircuit): Circuit to simulate.
    - `shots` (int): Number of simulation runs. Default: `1024`.
- **Returns**: `dict[str, int]` - Mapping of bitstring to count (e.g., `{"00": 512, "11": 512}`).

## Visualization Functions

### `circuit_to_ascii(circuit) -> str`

- **Description**: Render a quantum circuit as ASCII art. Gate symbols: H, X, Y, Z, Rx, Ry, Rz, CNOT target=X control=\*, CZ target=Z control=\*, SWAP=x, Measure=M.
- **Parameters**:
    - `circuit` (QuantumCircuit): The circuit to render.
- **Returns**: `str` - Multi-line ASCII art with one line per qubit wire.

### `circuit_stats(circuit) -> dict`

- **Description**: Return circuit statistics.
- **Parameters**:
    - `circuit` (QuantumCircuit): The circuit to analyze.
- **Returns**: `dict` with keys:
    - `num_qubits` (int): Number of qubits.
    - `num_gates` (int): Total gate count.
    - `gate_counts` (dict[str, int]): Count per gate type name.
    - `depth` (int): Maximum gates on any single qubit wire.
    - `has_measurements` (bool): Whether the circuit has measurements.

## Convenience Functions

### `bell_state() -> QuantumCircuit`

Returns a 2-qubit Bell state circuit (H on qubit 0, CNOT 0->1, measure all).

### `ghz_state(n) -> QuantumCircuit`

Returns an n-qubit GHZ state circuit (H on qubit 0, CNOT 0->i for all other qubits, measure all).

### `qft(n) -> QuantumCircuit`

Returns an n-qubit Quantum Fourier Transform circuit. Does not include measurement.

## Error Handling

No custom exception classes. Invalid qubit indices may produce `IndexError` during simulation. The simulator does not validate circuit correctness at construction time.

## Configuration

No external configuration. All parameters are passed at construction or call time.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent Directory**: [codomyrmex](../README.md)
