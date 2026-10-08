# LLM Module - MCP Tool Specification

This document defines the Model Context Protocol (MCP) tools for the `llm` module. They are defined with `@mcp_tool` in `mcp_tools.py` and surfaced by the PAI MCP bridge as `codomyrmex.<name>`.

## General Considerations for LLM Tools

- **Providers**: `ask` and `generate_text` (provider `openrouter`) call OpenRouter and need `OPENROUTER_API_KEY`. `generate_text` (provider `ollama`) and `list_local_models` need a local Ollama installation.
- **Not exposed as MCP tools**: Embeddings, RAG, guardrails, cost tracking and model pulls are available from the Python API only.
- **Error Handling**: Dictionary-returning tools return `{"status": "error", "message": "<description>"}`; `ask` returns a string starting with `"Error"`.
- **Security**: API keys are read from the environment and never returned. Prompts are sent to the selected provider.

---

## Tool: `generate_text`

### 1. Tool Purpose and Description

Generates text from a prompt with OpenRouter (through `ask`) or a local Ollama model.

### 2. Invocation Name

`generate_text`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `prompt` | `string` | Yes | Input prompt | `"Summarise the CAP theorem."` |
| `provider` | `string` | No | `"openrouter"` or `"ollama"` (default `"openrouter"`) | `"ollama"` |
| `model` | `string` | No | Model ID for the provider (default `"openrouter/free"`) | `"llama3.2"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` |
| `content` | `string` | Generated text (only on success) |
| `message` | `string` | Error description, e.g. `"Unsupported provider: <provider>"` |

### 5. Idempotency

- **Idempotent**: No; model output can differ between calls.

### 6. Usage Examples

```json
{
  "tool_name": "generate_text",
  "arguments": {"prompt": "Summarise the CAP theorem.", "provider": "ollama", "model": "llama3.2"}
}
```

---

## Tool: `list_local_models`

### 1. Tool Purpose and Description

Lists the models installed in the local Ollama instance.

### 2. Invocation Name

`list_local_models`

### 3. Input Schema (Parameters)

None.

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "models": ["llama3.2:latest"],
  "count": 1
}
```

On failure: `{"status": "error", "message": "Failed to list local models: <error>"}`.

---

## Tool: `query_fabric_metadata`

### 1. Tool Purpose and Description

Reports whether the Microsoft Fabric integration is configured and, if so, its workspace and tenant IDs.

### 2. Invocation Name

`query_fabric_metadata`

### 3. Input Schema (Parameters)

None.

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "configured": true,
  "workspace": "<workspace_id>",
  "tenant": "<tenant_id>"
}
```

When Fabric is not configured: `{"status": "success", "configured": false, "message": "Fabric is not configured currently."}`.

---

## Tool: `reason`

### 1. Tool Purpose and Description

Runs `ChainOfThought` on a prompt and returns its reasoning steps, conclusion and confidence.

### 2. Invocation Name

`reason`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `prompt` | `string` | Yes | Question or problem to reason about | `"Should this cache be write-through?"` |
| `depth` | `string` | No | `shallow`, `normal`, `deep` or `exhaustive`; unknown values use `normal` (default `"normal"`) | `"deep"` |
| `max_steps` | `integer` | No | Accepted for compatibility but not used by the current implementation (default `5`) | `5` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` |
| `steps` | `array[object]` | `{"step", "type", "content", "confidence"}` per reasoning step |
| `conclusion` | `string` | Concluding action |
| `confidence` | `number` | Overall confidence (0-1) |
| `step_count` | `integer` | Number of steps |
| `depth` | `string` | The `depth` argument as given |

---

## Tool: `ask`

### 1. Tool Purpose and Description

Sends one question to OpenRouter and returns the reply text.

### 2. Invocation Name

`ask`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `question` | `string` | Yes | Prompt to send | `"What is a monad?"` |
| `model` | `string` | No | OpenRouter model ID (default `"openrouter/free"`) | `"openrouter/free"` |

### 4. Output Schema (Return Value)

A plain string: the model's reply. Failures are also strings: `"Error: OPENROUTER_API_KEY not set in environment."` or `"Error querying LLM: <error>"`.

### 5. Security Considerations

- **Data Handling**: The question is sent to OpenRouter; do not include secrets.

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
