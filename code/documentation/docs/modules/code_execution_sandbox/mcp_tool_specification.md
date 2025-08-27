---
id: code-execution-sandbox-mcp-tool-specification
title: Code Execution Sandbox - MCP Tool Specification
sidebar_label: MCP Tool Specification
---

# Code Execution Sandbox - MCP Tool Specification

## Tool: `sandbox.execute_code`

### 1. Tool Purpose and Description

Allows an LLM or AI agent to securely execute a given code snippet in a specified language within an isolated sandbox. The tool returns the standard output, standard error, and exit code.

### 2. Invocation Name

`code_execution_sandbox.execute_code`

### 3. Input Schema (Parameters)

| Parameter Name | Type     | Required | Description                                                       | Example Value                               |
| :------------- | :------- | :------- | :---------------------------------------------------------------- | :------------------------------------------ |
| `language`     | `string` | Yes      | Programming language (e.g., `python`, `javascript`, `bash`).        | `"python"`                                  |
| `code`         | `string` | Yes      | The code snippet to execute.                                      | `"print('Hello from the sandbox!')"`        |
| `stdin_data`   | `string` | No       | Data to pass to the script's standard input.                      | `"some input data"`                         |
| `timeout_ms`   | `integer`| No       | Max execution time in milliseconds. Default: 5000 (5 seconds).    | `10000`                                     |

**JSON Schema Example:**
```json
{
  "type": "object",
  "properties": {
    "language": {
      "type": "string",
      "description": "Programming language (e.g., python, javascript, bash)."
    },
    "code": {
      "type": "string",
      "description": "The code snippet to execute."
    },
    "stdin_data": {
      "type": "string",
      "description": "Data to pass to the script's standard input."
    },
    "timeout_ms": {
      "type": "integer",
      "description": "Max execution time in milliseconds. Default: 5000.",
      "default": 5000
    }
  },
  "required": ["language", "code"]
}
```

### 4. Output Schema (Return Value)

| Field Name | Type     | Description                                                        | Example Value                               |
| :--------- | :------- | :----------------------------------------------------------------- | :------------------------------------------ |
| `stdout`   | `string` | Standard output from the executed code.                            | `"Hello from the sandbox!\n"`                |
| `stderr`   | `string` | Standard error output. Empty if no errors.                         | `""`                                        |
| `exit_code`| `integer`| Exit code of the script. `0` usually means success.                | `0`                                         |
| `status`   | `string` | `completed`, `timeout`, `error_runtime`, `error_setup`.            | `"completed"`                               |
| `duration_ms`| `integer`| Actual execution time in milliseconds.                             | `50`                                        |

**JSON Schema Example:**
```json
{
  "type": "object",
  "properties": {
    "stdout": { "type": "string" },
    "stderr": { "type": "string" },
    "exit_code": { "type": "integer" },
    "status": { "type": "string", "enum": ["completed", "timeout", "error_runtime", "error_setup"] },
    "duration_ms": { "type": "integer"}
  },
  "required": ["stdout", "stderr", "exit_code", "status", "duration_ms"]
}
```

### 5. Error Handling

- `UNSUPPORTED_LANGUAGE`: The requested `language` is not supported by the sandbox.
- `SANDBOX_SETUP_FAILED`: The sandbox environment could not be initialized.
- `EXECUTION_TIMEOUT`: Code execution exceeded the `timeout_ms`.
- `RUNTIME_ERROR`: The code executed but produced a runtime error (details in `stderr`).

### 6. Idempotency

- Generally idempotent if the executed code itself is idempotent and has no external side effects. The sandbox environment is typically fresh for each execution.
- Side Effects: None on the host system. Creates a temporary isolated environment for execution.

### 7. Usage Examples

**Example: Execute a Python snippet**
```json
{
  "tool_name": "code_execution_sandbox.execute_code",
  "arguments": {
    "language": "python",
    "code": "for i in range(3): print(f'Count: {i}')"
  }
}
```

### 8. Security Considerations

- **Core Security**: This tool is *the* primary defense against arbitrary code execution. The sandbox implementation (e.g., Docker, nsjail, Firecracker) must be robust and correctly configured to prevent escapes and unauthorized access to the host system or network.
- **Resource Limits**: Strict CPU, memory, time, and network restrictions are critical to prevent denial-of-service attacks or runaway scripts.
- **Language Runtimes**: Ensure language runtimes within the sandbox are patched and do not have known exploitable vulnerabilities.
- **Output Handling**: Sanitize or be cautious with `stdout` and `stderr` if they are displayed directly, as they could contain crafted output designed to exploit terminal emulators or UIs.

--- 