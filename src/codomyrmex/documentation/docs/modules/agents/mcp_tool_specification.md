# Agents - MCP Tool Specification

This document outlines the specification for tools within the Agents module that are integrated with the Model Context Protocol (MCP).

## 1. Overview

The `agents` module is the core framework for AI agent integration in Codomyrmex. It provides abstract interfaces, concrete client implementations for 12 providers (5 API, 6 CLI, 1 local), parsing utilities, and discovery/health-probing via `AgentRegistry`.

- **Configuration**: Agents may require API keys, model configurations, and capability settings.

---

## Tool: `execute_agent`

### 1. Tool Purpose and Description

Executes a request through a specified AI agent, returning the agent's response content.

### 2. Invocation Name

`execute_agent`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `agent_name` | `string` | Yes | Name of the agent to use (e.g., "claude", "gemini", "ollama") | `"claude"` |
| `prompt` | `string` | Yes | The prompt or instruction for the agent | `"Generate a Python function to calculate fibonacci numbers"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `content` | `string` | Generated content or response | `"def fibonacci(n): ..."` |
| `message` | `string` | Error message if status is `"error"` | `null` |

### 5. Error Handling

- **Agent Not Found**: Returns `{"status": "error", "message": "Agent '<name>' not found."}`
- **Execution Failure**: Returns `{"status": "error", "message": "Failed to execute agent <name>: <details>"}`

### 6. Idempotency

- **Idempotent**: No, responses may vary for the same prompt due to model non-determinism

### 7. Usage Examples

```json
{
  "tool_name": "execute_agent",
  "arguments": {
    "agent_name": "claude",
    "prompt": "Explain the difference between async and sync programming"
  }
}
```

### 8. Security Considerations

- **API Key Management**: Agent API keys should be stored securely and never logged
- **Input Sanitization**: Prompts should be validated to prevent injection attacks
- **Rate Limiting**: Implement rate limiting to prevent API abuse
- **Output Filtering**: Consider filtering responses for sensitive content

---

## Tool: `list_agents`

### 1. Tool Purpose and Description

Lists all available AI agents registered in the `AgentRegistry`, returning their descriptions and capabilities.

### 2. Invocation Name

`list_agents`

### 3. Input Schema (Parameters)

No parameters required.

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"success"` | `"success"` |
| `agents` | `array[object]` | List of available agents | See below |
| `count` | `integer` | Total number of agents | `11` |

### 5. Error Handling

- Returns empty list if no agents are configured

### 6. Idempotency

- **Idempotent**: Yes

---

## Tool: `get_agent_memory`

### 1. Tool Purpose and Description

Retrieve the interaction logs and memory for a specific agent session. Returns the most recent messages (up to 50) from the session history.

### 2. Invocation Name

`get_agent_memory`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `session_id` | `string` | Yes | The session ID to retrieve memory for | `"sess_abc123"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `session_id` | `string` | The queried session ID | `"sess_abc123"` |
| `logs` | `array[object]` | List of `{role, content}` message dicts | `[{"role": "user", "content": "..."}]` |

### 5. Error Handling

- **Session Not Found**: Returns `{"status": "error", "message": "Session <id> not found."}`
- **Retrieval Failure**: Returns `{"status": "error", "message": "Failed to retrieve memory for <id>: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
