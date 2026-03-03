# Agents Core -- MCP Tool Specification

This document specifies the MCP-discoverable tools exposed by the `agents/core` module. These tools provide Chain-of-Thought reasoning, thinking depth control, trace retrieval, and ReAct (Reasoning + Acting) capabilities through the ThinkingAgent.

## General Considerations

- **Auto-Discovery**: Tools use the `@mcp_tool(category="agents.core")` decorator and are auto-discovered via the MCP bridge.
- **Dependencies**: Requires the `agents.core` module's `ThinkingAgent`, `ReActAgent`, `ToolRegistry`, and `AgentRequest` classes, as well as `llm.models.reasoning.ThinkingDepth`.
- **Singleton Agent**: The `think`, `get_thinking_depth`, `set_thinking_depth`, and `get_last_trace` tools share a module-level `ThinkingAgent` singleton (lazily initialized on first call).
- **Error Handling**: All tools return `{"status": "error", "message": "..."}` on failure.

---

## Tool: `think`

### 1. Tool Purpose and Description

Run Chain-of-Thought reasoning on a prompt. Decomposes the prompt into structured reasoning steps and synthesizes a conclusion with confidence scoring.

### 2. Invocation Name

`think`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `prompt` | `string` | Yes | The question or problem to reason about | `"Should we use a microservice or monolith architecture for this project?"` |
| `depth` | `string` | No | Thinking depth (default: `"normal"`). One of: `"shallow"`, `"normal"`, `"deep"` | `"deep"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `content` | `string` | The reasoning conclusion or response content | `"Based on the analysis, a modular monolith is recommended because..."` |
| `confidence` | `number` | Overall confidence score (0.0--1.0) from the reasoning trace | `0.85` |
| `steps` | `integer` | Number of reasoning steps executed | `4` |
| `depth` | `string` | The thinking depth value that was used | `"normal"` |

### 5. Error Handling

- Invalid depth values fall back to `"normal"` silently (no error returned).
- ThinkingAgent initialization failures or execution errors propagate as exceptions.
- Missing `ThinkingDepth` or `AgentRequest` imports cause import errors at call time.

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: Reasoning may produce different outputs on repeated calls due to the non-deterministic nature of LLM-based thinking. The shared singleton also retains state (last trace) between calls.

### 7. Usage Examples

```json
{
  "tool_name": "think",
  "arguments": {
    "prompt": "What are the trade-offs of using Redis vs Memcached for session storage?",
    "depth": "deep"
  }
}
```

### 8. Security Considerations

- Prompts are passed directly to the ThinkingAgent. Callers should sanitize inputs to prevent prompt injection.
- Reasoning output may contain sensitive analysis. Handle results appropriately.

---

## Tool: `get_thinking_depth`

### 1. Tool Purpose and Description

Return the current thinking depth setting of the shared ThinkingAgent singleton.

### 2. Invocation Name

`get_thinking_depth`

### 3. Input Schema (Parameters)

This tool takes no parameters.

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` | `"success"` |
| `depth` | `string` | Current thinking depth value (`"shallow"`, `"normal"`, or `"deep"`) | `"normal"` |

### 5. Error Handling

- ThinkingAgent initialization failures propagate as exceptions.

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Reading the current depth does not modify any state.

### 7. Usage Examples

```json
{
  "tool_name": "get_thinking_depth",
  "arguments": {}
}
```

### 8. Security Considerations

- No sensitive data involved. This is a read-only introspection tool.

---

## Tool: `set_thinking_depth`

### 1. Tool Purpose and Description

Set the ThinkingAgent's reasoning depth. This affects all subsequent calls to the `think` tool on the shared singleton.

### 2. Invocation Name

`set_thinking_depth`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `depth` | `string` | Yes | One of: `"shallow"`, `"normal"`, `"deep"` | `"deep"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `depth` | `string` | The new thinking depth value | `"deep"` |
| `message` | `string` | Error description (only on error) | `"Unknown depth 'ultra'. Use 'shallow', 'normal', or 'deep'."` |

### 5. Error Handling

- Unknown depth values return an error status with a descriptive message listing valid options.
- ThinkingAgent initialization failures propagate as exceptions.

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Setting the same depth repeatedly produces the same final state.

### 7. Usage Examples

```json
{
  "tool_name": "set_thinking_depth",
  "arguments": {
    "depth": "shallow"
  }
}
```

### 8. Security Considerations

- This modifies the shared ThinkingAgent state. In multi-consumer scenarios, depth changes affect all subsequent callers.
- No sensitive data involved.

---

## Tool: `get_last_trace`

### 1. Tool Purpose and Description

Retrieve the most recent reasoning trace from the shared ThinkingAgent singleton. Returns detailed trace metadata including the trace ID, step count, confidence, completion status, and conclusion.

### 2. Invocation Name

`get_last_trace`

### 3. Input Schema (Parameters)

This tool takes no parameters.

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `trace_id` | `string` | Unique identifier for the trace | `"tr-a1b2c3d4"` |
| `depth` | `string` | Thinking depth used for this trace | `"normal"` |
| `steps` | `integer` | Number of reasoning steps | `3` |
| `confidence` | `number` | Overall confidence score (0.0--1.0) | `0.87` |
| `is_complete` | `boolean` | Whether the reasoning trace completed | `true` |
| `conclusion` | `object` | Conclusion details (see below) | `{"action": "...", "justification": "...", "confidence": 0.87}` |
| `message` | `string` | Error description (only on error) | `"No reasoning traces available."` |

The `conclusion` object contains:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `action` | `string \| null` | The recommended action |
| `justification` | `string \| null` | Reasoning behind the conclusion |
| `confidence` | `number \| null` | Conclusion-specific confidence score |

### 5. Error Handling

- If no traces exist (no prior `think` calls), returns `{"status": "error", "message": "No reasoning traces available."}`.
- ThinkingAgent initialization failures propagate as exceptions.

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Reading the last trace does not modify any state. Returns the same trace until a new `think` call is made.

### 7. Usage Examples

```json
{
  "tool_name": "get_last_trace",
  "arguments": {}
}
```

### 8. Security Considerations

- Trace data may contain sensitive reasoning about the original prompt. Handle results appropriately.
- The trace persists in memory on the singleton until replaced by a subsequent `think` call.

---

## Tool: `react_step`

### 1. Tool Purpose and Description

Execute a single ReAct (Reasoning + Acting) step. Given an observation, the agent reasons about what action to take and returns a thought + action pair. Uses a separate `ReActAgent` instance (not the shared ThinkingAgent singleton).

### 2. Invocation Name

`react_step`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `observation` | `string` | Yes | Current observation or task description | `"The test suite has 3 failing tests in the auth module"` |
| `available_tools` | `array[string] \| null` | No | List of tool names available for actions. Defaults to `["search", "think", "calculate", "conclude"]` if not provided. | `["search", "read_file", "run_tests"]` |
| `max_steps` | `integer` | No | Maximum number of steps before forced conclusion (default: `5`) | `3` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` | `"success"` |
| `thought` | `string` | The agent's reasoning about the observation | `"Given observation '...', considering available actions: [...]"` |
| `action` | `string` | The chosen action (tool name) | `"search"` |
| `action_input` | `string` | Input to pass to the chosen action | `"The test suite has 3 failing tests in the auth module"` |
| `is_final` | `boolean` | Whether this is the final step (conclusion reached) | `false` |
| `step_number` | `integer` | Current step number in the ReAct loop | `1` |
| `content` | `string` | Full response content from the agent (only on success with agent) | `"..."` |
| `note` | `string` | Exception message (only on fallback path) | `"ReActAgent import failed"` |

### 5. Error Handling

- This tool has a graceful fallback: if the `ReActAgent` or `ToolRegistry` cannot be imported, it returns a synthetic thought/action pair with a `note` field describing the error. The status remains `"success"` in the fallback path.
- The available tools are registered as no-op placeholders for the agent's planning; they are not actually executed.

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: Each call creates a new `ReActAgent` instance. Reasoning output is non-deterministic due to LLM-based thinking.

### 7. Usage Examples

```json
{
  "tool_name": "react_step",
  "arguments": {
    "observation": "The API endpoint returns 500 errors intermittently",
    "available_tools": ["search", "read_file", "run_tests", "think"],
    "max_steps": 3
  }
}
```

### 8. Security Considerations

- Tool names in `available_tools` are registered as no-op functions. The ReAct agent plans with them but does not execute them through this tool.
- Observations are passed directly to the ReAct agent. Sanitize inputs to prevent prompt injection.
- Each call creates a fresh agent instance, so there is no state leakage between calls.

---

## Navigation Links

- **Parent**: [Module README](./README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Home**: [Root README](../../../README.md)
