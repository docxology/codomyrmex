# Simulation - MCP Tool Specification

This document outlines the specification for tools within the Simulation module that are intended to be integrated with the Model Context Protocol (MCP).

## General Considerations

- **Dependencies**: Requires the `logging_monitoring` module. Ensure `setup_logging()` is called.
- **Initialization**: A `Simulator` instance must be created (optionally with `SimulationConfig`) before tools can execute.
- **Error Handling**: Errors are logged using `logging_monitoring`. Tools return an `{"error": "description"}` object on failure.

---

## Tool: `simulation_run`

### 1. Tool Purpose and Description

Executes a full simulation run with the given configuration parameters, returning structured results upon completion. This is the primary tool for running simulations via MCP.

### 2. Invocation Name

`simulation_run`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `name` | `string` | No | Simulation name identifier (default: "default_simulation") | `"my_experiment"` |
| `max_steps` | `integer` | No | Maximum steps to execute (default: 1000) | `500` |
| `seed` | `integer` | No | Random seed for reproducibility (default: null) | `42` |
| `params` | `object` | No | Arbitrary model-specific parameters (default: {}) | `{"learning_rate": 0.01}` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `steps_completed` | `integer` | Number of steps executed | `500` |
| `config` | `string` | Simulation configuration name | `"my_experiment"` |
| `simulation_status` | `string` | `"completed"` or `"running"` | `"completed"` |

### 5. Error Handling

- **Step Failure**: Returns error with the step number at which the simulation failed and the exception message.
- **Invalid Configuration**: Returns error if `max_steps` is not a positive integer.

### 6. Idempotency

- **Idempotent**: Yes, when using the same `seed` and `params`. Running with the same configuration and seed produces identical results.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "simulation_run",
  "arguments": {
    "name": "agent_experiment",
    "max_steps": 500,
    "seed": 42,
    "params": {
      "population": 100,
      "decay_rate": 0.95
    }
  }
}
```

### 8. Security Considerations

- **Input Validation**: `max_steps` is validated as a positive integer. `name` is validated as a non-empty string. `params` values are type-checked where applicable.
- **Permissions**: No file system or network access required for base simulation execution.
- **Data Handling**: Simulation parameters and results do not contain sensitive data by default.
- **Resource Limits**: `max_steps` provides an upper bound to prevent unbounded execution.

---

## Tool: `simulation_get_results`

### 1. Tool Purpose and Description

Retrieves the current results from a simulation instance. Useful for checking simulation state after step-by-step execution or verifying completed run outcomes.

### 2. Invocation Name

`simulation_get_results`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `name` | `string` | Yes | Name of the simulation to retrieve results for | `"my_experiment"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `steps_completed` | `integer` | Number of steps executed | `500` |
| `config` | `string` | Simulation configuration name | `"my_experiment"` |
| `simulation_status` | `string` | `"completed"` or `"running"` | `"completed"` |

### 5. Error Handling

- **Simulation Not Found**: Returns error if no simulation with the given name exists.

### 6. Idempotency

- **Idempotent**: Yes. Repeated calls return the same results without side effects.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "simulation_get_results",
  "arguments": {
    "name": "agent_experiment"
  }
}
```

### 8. Security Considerations

- **Input Validation**: `name` is validated as a non-empty string.
- **Permissions**: Read-only operation; no file system or network access.
- **Data Handling**: Returns only simulation metadata and step counts.

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
