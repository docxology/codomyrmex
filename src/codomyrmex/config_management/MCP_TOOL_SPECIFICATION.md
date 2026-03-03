# Configuration Management -- MCP Tool Specification

This document specifies the MCP-discoverable tools exposed by the `config_management` module. These tools provide configuration retrieval, mutation, and validation through the MCP bridge.

## General Considerations

- **Auto-Discovery**: Tools use the `@mcp_tool(category="config_management")` decorator and are auto-discovered via the MCP bridge.
- **Dependencies**: Requires the `config_management` module's internal `get_config`, `set_config`, and `validate_config` functions.
- **Error Handling**: All tools return `{"status": "error", "message": "..."}` on failure.

---

## Tool: `get_config`

### 1. Tool Purpose and Description

Retrieve a configuration value by key from a specified namespace. Returns the value along with its key and namespace metadata.

### 2. Invocation Name

`get_config`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `key` | `string` | Yes | Configuration key to look up | `"log_level"` |
| `namespace` | `string` | No | Configuration namespace (default: `"default"`). Examples: `"default"`, `"llm"`, `"mcp"` | `"llm"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `key` | `string` | The configuration key that was looked up | `"log_level"` |
| `namespace` | `string` | The namespace searched | `"default"` |
| `value` | `any` | The configuration value (type depends on the stored value) | `"INFO"` |
| `message` | `string` | Error description (only on error) | `"Key 'foo' not found in namespace 'default'"` |

### 5. Error Handling

- Missing keys return an error status with the exception message from the config backend.
- Invalid namespace names return an error status.

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Reading a configuration value does not modify any state. The same key and namespace always return the current value.

### 7. Usage Examples

```json
{
  "tool_name": "get_config",
  "arguments": {
    "key": "model_provider",
    "namespace": "llm"
  }
}
```

### 8. Security Considerations

- Configuration values may contain sensitive data (API keys, connection strings). Callers should handle returned values with care.
- The tool does not distinguish between sensitive and non-sensitive keys. Access control should be enforced at the MCP bridge or trust gateway level.

---

## Tool: `set_config`

### 1. Tool Purpose and Description

Set a configuration value for a given key in a specified namespace. Overwrites any existing value for that key.

### 2. Invocation Name

`set_config`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `key` | `string` | Yes | Configuration key to set | `"log_level"` |
| `value` | `any` | Yes | Value to store (string, number, boolean, object, or array) | `"DEBUG"` |
| `namespace` | `string` | No | Configuration namespace (default: `"default"`) | `"llm"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `key` | `string` | The configuration key that was set | `"log_level"` |
| `namespace` | `string` | The namespace used | `"default"` |
| `updated` | `boolean` | Confirmation that the value was written | `true` |
| `message` | `string` | Error description (only on error) | `"Permission denied for namespace 'system'"` |

### 5. Error Handling

- Invalid keys or namespaces return an error status.
- Backend write failures (e.g., permission issues, validation errors) return an error status with the exception message.

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Setting the same key to the same value produces the same final state. Repeated calls with identical arguments are safe.

### 7. Usage Examples

```json
{
  "tool_name": "set_config",
  "arguments": {
    "key": "max_retries",
    "value": 3,
    "namespace": "mcp"
  }
}
```

### 8. Security Considerations

- This is a write operation. It should be gated by the trust gateway at TRUSTED level or higher.
- Callers should avoid storing secrets through this tool; use dedicated secret management instead.
- Configuration changes may affect runtime behavior of other modules immediately.

---

## Tool: `validate_config`

### 1. Tool Purpose and Description

Validate configuration consistency and completeness for a given namespace. Returns a report detailing any issues found.

### 2. Invocation Name

`validate_config`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `namespace` | `string` | No | Configuration namespace to validate (default: `"default"`) | `"llm"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `namespace` | `string` | The namespace that was validated | `"default"` |
| `valid` | `boolean` | Whether the configuration is valid | `true` |
| `issues` | `array` | List of issue descriptions (empty if valid) | `["Missing required key: api_endpoint"]` |
| `message` | `string` | Error description (only on error) | `"Validation backend unavailable"` |

### 5. Error Handling

- Validation backend failures return an error status with the exception message.
- Invalid namespace names return an error status.

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Validation is a read-only operation that inspects the current configuration state without modifying it.

### 7. Usage Examples

```json
{
  "tool_name": "validate_config",
  "arguments": {
    "namespace": "mcp"
  }
}
```

### 8. Security Considerations

- Validation results may reveal information about configuration structure and expected keys. Handle results appropriately.
- This is a read-only operation and does not require elevated trust levels.

---

## Navigation Links

- **Parent**: [Module README](./README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Home**: [Root README](../../../README.md)
