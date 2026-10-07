# Quantum - MCP Tool Specification

## General Considerations for Quantum Tools

- **Registration**: Tools are defined with `@mcp_tool` in `mcp_tools.py` and surfaced by the PAI MCP bridge as `codomyrmex.<name>`.
- **Dependencies**: No external dependencies. Uses only Python standard library (`cmath`, `math`, `random`).
- **Initialization**: `QuantumSimulator` is instantiated per call. No persistent state between calls.
- **Error Handling**: Invalid circuits raise `ValueError` (for example `"Invalid gate type: <type>"`, `"Gate requires a target qubit"`, `"CNOT gate requires a control qubit"`), which surfaces as a tool error.
- **Performance**: Statevector simulation scales as O(2^n) in memory. Practical limit is approximately 20 qubits.

### Circuit format

`circuit_data` is an object with:

| Field | Type | Description |
| :--- | :--- | :--- |
| `num_qubits` | `integer` | Number of qubits (default `1`) |
| `gates` | `array[object]` | Gates in order: `{"gate_type", "target", "control"?, "parameter"?}` |
| `measure_all` | `boolean` | Add a measurement on every qubit (default `false`) |

`gate_type` is case-insensitive and applied for `H`, `X`, `Y`, `Z`, `CNOT`, `CZ`, `SWAP` (these three need `control`) and `RX`, `RY`, `RZ` (these need `parameter`, an angle in radians). `T` and `S` are accepted but not applied, and gates without `gate_type` are skipped.

---

## Tool: `quantum_run_circuit`

### 1. Tool Purpose and Description

Builds a circuit from `circuit_data`, simulates it `shots` times and returns measurement counts.

### 2. Invocation Name

`quantum_run_circuit`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `circuit_data` | `object` | Yes | Circuit definition (see [Circuit format](#circuit-format)) | see example |
| `shots` | `integer` | No | Number of simulation runs (default `1024`) | `100` |

### 4. Output Schema (Return Value)

An object mapping measured bitstrings to counts, e.g. `{"00": 54, "11": 46}`.

### 5. Usage Examples

```json
{
  "tool_name": "quantum_run_circuit",
  "arguments": {
    "circuit_data": {
      "num_qubits": 2,
      "gates": [
        {"gate_type": "H", "target": 0},
        {"gate_type": "CNOT", "control": 0, "target": 1}
      ],
      "measure_all": true
    },
    "shots": 100
  }
}
```

---

## Tool: `quantum_circuit_stats`

### 1. Tool Purpose and Description

Builds a circuit from `circuit_data` and returns its statistics without simulating it.

### 2. Invocation Name

`quantum_circuit_stats`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `circuit_data` | `object` | Yes | Circuit definition (see [Circuit format](#circuit-format)) | see `quantum_run_circuit` |

### 4. Output Schema (Return Value)

```json
{
  "num_qubits": 2,
  "num_gates": 2,
  "gate_counts": {"H": 1, "CNOT": 1},
  "depth": 2,
  "has_measurements": true
}
```

---

## Tool: `quantum_bell_state_demo`

### 1. Tool Purpose and Description

Simulates the two-qubit Bell state circuit (H then CNOT, measured) and returns counts, an ASCII drawing and circuit statistics.

### 2. Invocation Name

`quantum_bell_state_demo`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `shots` | `integer` | No | Number of simulation runs (default `1024`) | `100` |

### 4. Output Schema (Return Value)

```json
{
  "counts": {"00": 54, "11": 46},
  "ascii_circuit": "q0: -H--*--M-\nq1: ----X--M-",
  "stats": {
    "num_qubits": 2,
    "num_gates": 2,
    "gate_counts": {"H": 1, "CNOT": 1},
    "depth": 2,
    "has_measurements": true
  }
}
```

---

## Navigation Links

- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Human Documentation**: [README.md](README.md)
- **Parent Directory**: [codomyrmex](../README.md)

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
