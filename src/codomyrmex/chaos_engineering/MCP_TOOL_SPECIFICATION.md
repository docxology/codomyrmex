# Chaos Engineering - MCP Tool Specification

This document defines the Model Context Protocol tools for the Chaos Engineering module, covering fault injection, experiment execution, and status monitoring.

## General Considerations

- **Safety**: Chaos tools inject real failures. Use only in controlled environments (staging, testing).
- **Rollback**: Experiments with rollback actions will automatically clean up after execution.
- **Probabilistic**: Fault injection is probability-based; a single invocation may or may not trigger the fault.

---

## Tool: `chaos_inject_fault`

### 1. Tool Purpose and Description

Registers and optionally triggers a fault injection by name. Can register a new fault configuration or trigger an existing one.

### 2. Invocation Name

`chaos_inject_fault`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `fault_name` | `string` | Yes | Unique fault identifier | `"slow-database"` |
| `action` | `string` | Yes | `"register"`, `"inject"`, `"remove"` | `"register"` |
| `fault_type` | `string` | No | Required for `register`: `"latency"`, `"error"`, `"timeout"`, `"resource_exhaustion"`, `"network_partition"` | `"latency"` |
| `probability` | `number` | No | Injection probability 0.0-1.0 (default: 0.1) | `0.5` |
| `duration_seconds` | `number` | No | Duration for latency/timeout faults | `2.0` |
| `error_message` | `string` | No | Error message for error/timeout faults | `"DB unavailable"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"registered"`, `"injected"`, `"removed"`, or `"error"` | `"registered"` |
| `fault_name` | `string` | Fault identifier | `"slow-database"` |
| `fault_type` | `string` | Type of fault | `"latency"` |
| `was_triggered` | `boolean` | Whether fault was actually triggered (for `inject`) | `true` |

### 5. Error Handling

- **Fault Not Found**: `inject` or `remove` on non-existent fault returns error.
- **Missing Parameters**: `register` without `fault_type` returns error.
- **Invalid Probability**: Values outside 0.0-1.0 return error.

### 6. Idempotency

- **register**: Idempotent (overwrites existing config).
- **inject**: Not idempotent (probabilistic side effects).
- **remove**: Idempotent (removing non-existent fault returns success).

### 7. Usage Examples

```json
{
  "tool_name": "chaos_inject_fault",
  "arguments": {
    "fault_name": "slow-database",
    "action": "register",
    "fault_type": "latency",
    "probability": 0.3,
    "duration_seconds": 2.0
  }
}
```

```json
{
  "tool_name": "chaos_inject_fault",
  "arguments": {
    "fault_name": "slow-database",
    "action": "inject"
  }
}
```

### 8. Security Considerations

- **Destructive**: Fault injection can cause service degradation. Restrict to non-production environments.
- **Authorization**: Require elevated permissions for fault registration and injection.
- **Audit Logging**: All fault injections should be logged for post-incident review.

---

## Tool: `chaos_run_experiment`

### 1. Tool Purpose and Description

Runs a chaos experiment: verifies steady state, executes the chaos action, re-verifies steady state, and performs rollback if configured.

### 2. Invocation Name

`chaos_run_experiment`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `experiment_name` | `string` | Yes | Name of the experiment to run | `"kill-cache"` |
| `dry_run` | `boolean` | No | Validate without executing action (default: false) | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `experiment_name` | `string` | Experiment that ran | `"kill-cache"` |
| `success` | `boolean` | System maintained steady state | `true` |
| `steady_state_before` | `boolean` | Steady state verified before action | `true` |
| `steady_state_after` | `boolean` | Steady state verified after action | `true` |
| `duration_seconds` | `number` | Total experiment duration | `5.3` |
| `error` | `string\|null` | Error details if any | `null` |
| `started_at` | `string` | ISO timestamp | `"2026-02-05T10:00:00Z"` |

### 5. Error Handling

- **Experiment Not Found**: Returns error if experiment_name is not registered.
- **Pre-check Failure**: Returns `success: false` with `steady_state_before: false` if system is not in steady state before the experiment.
- **Rollback Failure**: Error string includes rollback failure details appended after a semicolon.

### 6. Idempotency

- **Not Idempotent**: Experiments have side effects (fault injection, rollback).

### 7. Usage Examples

```json
{
  "tool_name": "chaos_run_experiment",
  "arguments": {
    "experiment_name": "kill-cache",
    "dry_run": false
  }
}
```

### 8. Security Considerations

- **Controlled Execution**: Experiments should only run in designated environments.
- **Rollback Guarantee**: Always configure rollback actions for experiments that modify infrastructure.
- **Timeout**: Long-running experiments should have external timeout enforcement.

---

## Tool: `chaos_status`

### 1. Tool Purpose and Description

Returns the current state of the chaos engineering system: active faults, registered experiments, and historical results.

### 2. Invocation Name

`chaos_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `include_results` | `boolean` | No | Include historical experiment results (default: false) | `true` |
| `experiment_name` | `string` | No | Filter to specific experiment | `"kill-cache"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `active_faults` | `array[object]` | Currently registered faults | See below |
| `registered_experiments` | `integer` | Number of registered experiments | `3` |
| `results` | `array[object]` | Historical results (if requested) | See ExperimentResult schema |
| `total_runs` | `integer` | Total experiments executed | `12` |
| `success_rate` | `number` | Percentage of successful experiments | `0.83` |

Each fault object:

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `name` | `string` | Fault name | `"slow-database"` |
| `fault_type` | `string` | Fault type | `"latency"` |
| `probability` | `number` | Injection probability | `0.3` |

### 5. Error Handling

- Returns empty arrays if no faults or experiments are registered.

### 6. Idempotency

- **Idempotent**: Yes. Read-only query.

### 7. Usage Examples

```json
{
  "tool_name": "chaos_status",
  "arguments": {
    "include_results": true
  }
}
```

### 8. Security Considerations

- Read-only operation. Fault configurations may reveal resilience testing strategies.

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Home**: [Root README](../../../README.md)
