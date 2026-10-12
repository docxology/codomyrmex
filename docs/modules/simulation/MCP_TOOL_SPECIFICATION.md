# Simulation - MCP Tool Specification

This document specifies the Model Context Protocol (MCP) tools of the Simulation module. They are defined with `@mcp_tool` in `mcp_tools.py` and surfaced by the PAI MCP bridge as `codomyrmex.<name>`.

## General Considerations

- **No shared state**: Each call creates a new `Simulator` from its arguments. `simulation_status` therefore reports a fresh simulator (no agents, step `0`), not the result of an earlier `simulation_run`.
- **Error Handling**: Tools catch exceptions and return `{"status": "error", "message": "<description>"}`.
- **Method tool**: `simulator.py` also decorates the method `Simulator.run` (registered as `Simulator.run`). It needs a `Simulator` instance, so use it from Python rather than through MCP.

---

## Tool: `simulation_run`

### 1. Tool Purpose and Description

Creates a simulation with `agent_count` random agents and runs it for up to `max_steps` steps.

### 2. Invocation Name

`simulation_run`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `name` | `string` | No | Simulation name (default `"default"`) | `"my_experiment"` |
| `max_steps` | `integer` | No | Maximum steps to execute (default `100`) | `500` |
| `agent_count` | `integer` | No | Number of `RandomAgent`s to create (default `3`) | `5` |
| `agent_action_types` | `array[string]` | No | Actions the agents choose from (default `["move", "wait", "observe"]`) | `["move", "wait"]` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `steps_completed` | `integer` | Number of steps executed | `500` |
| `agent_count` | `integer` | Number of agents in the run | `5` |
| `config_name` | `string` | Simulation name | `"my_experiment"` |

### 5. Idempotency

- **Idempotent**: No; agents act randomly.

### 6. Usage Examples (for MCP context)

```json
{
  "tool_name": "simulation_run",
  "arguments": {
    "name": "agent_experiment",
    "max_steps": 500,
    "agent_count": 5
  }
}
```

---

## Tool: `simulation_status`

### 1. Tool Purpose and Description

Builds a simulator with the given configuration and reports its settings and readiness.

### 2. Invocation Name

`simulation_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `name` | `string` | No | Simulation name (default `"default"`) | `"my_experiment"` |
| `max_steps` | `integer` | No | Configured maximum steps (default `100`) | `500` |

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "config_name": "my_experiment",
  "max_steps": 500,
  "agent_count": 0,
  "step_count": 0
}
```

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `simulation_list_agents`

### 1. Tool Purpose and Description

Lists the simulation agent types with one-line descriptions.

### 2. Invocation Name

`simulation_list_agents`

### 3. Input Schema (Parameters)

None.

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "agent_types": [
    {"name": "RandomAgent", "description": "Acts randomly from a pool of action types."},
    {"name": "RuleBasedAgent", "description": "Executes prioritized condition-to-action rules."},
    {"name": "QLearningAgent", "description": "Tabular Q-learning with epsilon-greedy exploration."}
  ]
}
```

### 5. Idempotency

- **Idempotent**: Yes

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
