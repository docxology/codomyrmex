# Agents - MCP Tool Specification

This document outlines the specification for tools within the Agents module that are intended to be integrated with the Model Context Protocol (MCP).

## 1. Overview

The `agents` module is the core framework for AI agent integration in Codomyrmex. It provides abstract interfaces, concrete client implementations for 12 providers (5 API, 6 CLI, 1 local), parsing utilities, and discovery/health-probing via `AgentRegistry`.

- **Configuration**: Agents may require API keys, model configurations, and capability settings.

---

## Tool: `execute_agent_request`

### 1. Tool Purpose and Description

Executes a request through a specified AI agent, supporting various capabilities like code generation, code editing, text completion, and multi-turn conversations.

### 2. Invocation Name

`execute_agent_request`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `agent_name` | `string` | Yes | Name of the agent to use (e.g., "claude", "codex", "o1", "deepseek", "qwen", "gemini", "ollama") | `"claude"` |
| `prompt` | `string` | Yes | The prompt or instruction for the agent | `"Generate a Python function to calculate fibonacci numbers"` |
| `context` | `object` | No | Additional context for the request (e.g., language, file contents) | `{"language": "python", "existing_code": "..."}` |
| `capabilities` | `array[string]` | No | Required capabilities (e.g., "code_generation", "streaming") | `["code_generation"]` |
| `timeout` | `integer` | No | Request timeout in seconds | `30` |
| `config` | `object` | No | Agent-specific configuration overrides | `{"temperature": 0.7}` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | Status: "success", "error" | `"success"` |
| `content` | `string` | Generated content or response | `"def fibonacci(n): ..."` |
| `error` | `string` | Error message if status is "error" | `null` |
| `execution_time` | `number` | Time taken in seconds | `2.5` |
| `tokens_used` | `integer` | Number of tokens consumed | `150` |
| `metadata` | `object` | Additional response metadata | `{"model": "claude-3"}` |

### 5. Error Handling

- **Agent Not Found**: Returns error if specified agent is not available
- **Capability Mismatch**: Warning if requested capabilities are not supported
- **Timeout**: Returns error if request exceeds timeout limit
- **API Errors**: Propagates underlying API errors with context

### 6. Idempotency

- **Idempotent**: No, responses may vary for the same prompt due to model non-determinism

### 7. Usage Examples

```json
{
  "tool_name": "execute_agent_request",
  "arguments": {
    "agent_name": "claude",
    "prompt": "Explain the difference between async and sync programming",
    "capabilities": ["text_completion"],
    "timeout": 30
  }
}
```

### 8. Security Considerations

- **API Key Management**: Agent API keys should be stored securely and never logged
- **Input Sanitization**: Prompts should be validated to prevent injection attacks
- **Rate Limiting**: Implement rate limiting to prevent API abuse
- **Output Filtering**: Consider filtering responses for sensitive content

---

## Tool: `list_available_agents`

### 1. Tool Purpose and Description

Lists all available AI agents and their capabilities, helping users discover what agents can be used.

### 2. Invocation Name

`list_available_agents`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `capability_filter` | `string` | No | Filter agents by specific capability | `"code_generation"` |
| `include_status` | `boolean` | No | Include connection status for each agent | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `agents` | `array[object]` | List of available agents | See below |
| `total_count` | `integer` | Total number of agents | `11` |

**Agent object structure** (powered by `AgentRegistry.probe_all()`):

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `name` | `string` | Agent identifier |
| `capabilities` | `array[string]` | Supported capabilities |
| `status` | `string` | Connection status (if requested) |
| `description` | `string` | Human-readable description |

### 5. Error Handling

- Returns empty list if no agents are configured

### 6. Idempotency

- **Idempotent**: Yes

---

## Tool: `probe_agent_status`

### 1. Tool Purpose and Description

Probes a specific agent's health using `AgentRegistry.probe_agent()`. Returns real connectivity status (API key present, CLI binary found, Ollama server reachable).

### 2. Invocation Name

`probe_agent_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `agent_name` | `string` | Yes | Agent to probe | `"claude"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `name` | `string` | Agent identifier | `"claude"` |
| `status` | `string` | `"operative"`, `"key_missing"`, `"unreachable"`, `"unavailable"` | `"operative"` |
| `detail` | `string` | Human-readable explanation | `"Key present (ANTHROPIC_API_KEY=sk-a...)"` |
| `latency_ms` | `number` | Probe response time | `0.12` |

### 5. Error Handling

- Unknown agent returns `"unavailable"` status

### 6. Idempotency

- **Idempotent**: Yes

---

## Tool: `register_tool_with_agent`

### 1. Tool Purpose and Description

Registers a tool function with the agent's tool registry, allowing the agent to use it during execution.

### 2. Invocation Name

`register_tool_with_agent`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `tool_name` | `string` | Yes | Name for the tool | `"calculate"` |
| `tool_spec` | `object` | Yes | Tool specification including function and schema | See below |
| `agent_name` | `string` | No | Specific agent to register with (default: all) | `"react-agent"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `status` | `string` | "success" or "error" |
| `registered_with` | `array[string]` | List of agents the tool was registered with |

### 5. Error Handling

- **Invalid Schema**: Returns error if tool specification is malformed
- **Duplicate Tool**: Warning if tool name already exists (overwrites)

### 6. Idempotency

- **Idempotent**: Yes, repeated registration overwrites existing

---

## Navigation Links

- **Parent**: [Agents Module](README.md)
- **Module Index**: [All Modules](../AGENTS.md)
- **Documentation**: [Reference Guides](../README.md)
- **Home**: [Root README](../../../README.md)
