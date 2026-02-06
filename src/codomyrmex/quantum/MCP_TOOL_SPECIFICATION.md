# Quantum - MCP Tool Specification

## General Considerations for Quantum Tools

- **Dependencies**: No external dependencies. Uses only Python standard library (`cmath`, `math`, `random`).
- **Initialization**: `QuantumSimulator` is instantiated per-request. No persistent state between calls.
- **Error Handling**: Tools return `{"error": "description"}` on failure. Invalid qubit indices produce an error response.
- **Performance**: Statevector simulation scales as O(2^n) in memory. Practical limit is approximately 20 qubits.

---

## Tool: `quantum_simulate`

### 1. Tool Purpose and Description

Runs a quantum circuit simulation for a specified number of shots and returns measurement probability distributions as bitstring counts.

### 2. Invocation Name

`quantum_simulate`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `circuit` | `object` | Yes | Circuit definition (see `quantum_create_circuit` output) | See below |
| `shots` | `integer` | No | Number of simulation runs. Default: `1024` | `4096` |

The `circuit` object schema:

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `num_qubits` | `integer` | Yes | Number of qubits |
| `gates` | `array[object]` | Yes | Ordered list of `{gate_type, target, control?, parameter?}` |
| `measure_all` | `boolean` | No | Measure all qubits. Default: `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `counts` | `object` | Bitstring to count mapping | `{"00": 510, "11": 514}` |
| `shots` | `integer` | Total shots executed | `1024` |
| `num_qubits` | `integer` | Number of qubits in the circuit | `2` |

### 5. Error Handling

- `INVALID_CIRCUIT`: Circuit definition is malformed.
- `QUBIT_OUT_OF_RANGE`: A gate references a qubit index outside the circuit range.
- `SIMULATION_ERROR`: Runtime error during statevector computation.

### 6. Idempotency

- **Idempotent**: No. Measurement outcomes are probabilistic. Results vary between runs.

### 7. Usage Examples

```json
{
  "tool_name": "quantum_simulate",
  "arguments": {
    "circuit": {
      "num_qubits": 2,
      "gates": [
        {"gate_type": "H", "target": 0},
        {"gate_type": "CNOT", "target": 1, "control": 0}
      ],
      "measure_all": true
    },
    "shots": 1024
  }
}
```

### 8. Security Considerations

- **Resource Limits**: Circuits with more than 20 qubits may exhaust memory. Callers should validate qubit count.
- **Data Handling**: No file system or network access. Pure computation.

---

## Tool: `quantum_create_circuit`

### 1. Tool Purpose and Description

Builds a quantum circuit from a high-level description. Supports named circuit templates (bell, ghz, qft) or custom gate sequences. Returns a circuit object suitable for `quantum_simulate`.

### 2. Invocation Name

`quantum_create_circuit`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `template` | `string` | No | Named template: `"bell"`, `"ghz"`, or `"qft"` | `"bell"` |
| `num_qubits` | `integer` | Conditional | Required for `ghz`, `qft`, or custom circuits | `3` |
| `gates` | `array[object]` | No | Custom gate list. Each: `{gate_type, target, control?, parameter?}` | See below |
| `measure_all` | `boolean` | No | Add measurement to all qubits. Default: `true` | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `num_qubits` | `integer` | Number of qubits | `2` |
| `num_gates` | `integer` | Total gates in circuit | `3` |
| `gates` | `array[object]` | Gate list with `{gate_type, target, control?, parameter?}` | See below |
| `measurements` | `object` | Qubit-to-classical-bit mapping | `{"0": 0, "1": 1}` |

### 5. Error Handling

- `UNKNOWN_TEMPLATE`: Template name is not recognized.
- `MISSING_NUM_QUBITS`: `num_qubits` is required but was not provided.
- `INVALID_GATE`: A gate definition is malformed.

### 6. Idempotency

- **Idempotent**: Yes. Same inputs always produce the same circuit.

### 7. Usage Examples

```json
{
  "tool_name": "quantum_create_circuit",
  "arguments": {
    "template": "ghz",
    "num_qubits": 4
  }
}
```

```json
{
  "tool_name": "quantum_create_circuit",
  "arguments": {
    "num_qubits": 2,
    "gates": [
      {"gate_type": "H", "target": 0},
      {"gate_type": "RZ", "target": 1, "parameter": 1.5708},
      {"gate_type": "CNOT", "target": 1, "control": 0}
    ]
  }
}
```

### 8. Security Considerations

- **Input Validation**: Gate types are validated against the `GateType` enum. Unknown types are rejected.
- **Resource Limits**: `num_qubits` should be capped by the caller to prevent memory exhaustion.

---

## Tool: `quantum_measure`

### 1. Tool Purpose and Description

Measures specific qubits in a previously simulated circuit state, returning collapsed measurement results. Useful for partial measurement scenarios.

### 2. Invocation Name

`quantum_measure`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `circuit` | `object` | Yes | Circuit definition to simulate | See `quantum_create_circuit` |
| `qubits` | `array[integer]` | No | Specific qubit indices to measure. Default: all | `[0, 2]` |
| `shots` | `integer` | No | Number of measurement shots. Default: `1024` | `512` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `counts` | `object` | Bitstring to count mapping (only measured qubits) | `{"00": 256, "01": 256, "10": 256, "11": 256}` |
| `measured_qubits` | `array[integer]` | Qubit indices that were measured | `[0, 2]` |
| `shots` | `integer` | Total shots | `512` |

### 5. Error Handling

- `QUBIT_OUT_OF_RANGE`: Requested qubit index exceeds circuit size.
- `INVALID_CIRCUIT`: Circuit definition is malformed.

### 6. Idempotency

- **Idempotent**: No. Measurement results are probabilistic.

### 7. Usage Examples

```json
{
  "tool_name": "quantum_measure",
  "arguments": {
    "circuit": {
      "num_qubits": 3,
      "gates": [
        {"gate_type": "H", "target": 0},
        {"gate_type": "CNOT", "target": 1, "control": 0},
        {"gate_type": "CNOT", "target": 2, "control": 0}
      ]
    },
    "qubits": [0, 1],
    "shots": 2048
  }
}
```

### 8. Security Considerations

- **Resource Limits**: Same O(2^n) memory constraint as `quantum_simulate`.
- **Data Handling**: No state persisted between calls. No file system or network access.

---

## Navigation Links

- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Human Documentation**: [README.md](README.md)
- **Parent Directory**: [codomyrmex](../README.md)
