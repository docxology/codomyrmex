# CLI Module - MCP Tool Specification

This document defines the Model Context Protocol (MCP) tools for the `cli` module, which serves as the primary command-line interface entry point for the Codomyrmex platform. The tools are defined with `@mcp_tool` in `mcp_tools.py` and surfaced by the PAI MCP bridge as `codomyrmex.<name>`.

## General Considerations for CLI Tools

- **Scope**: Two tools wrap the `codomyrmex.cli.core.Cli` class: one lists its public commands, the other calls one of them by name. There are no per-command MCP tools.
- **Error Handling**: Both tools catch exceptions and return `{"status": "error", "message": "<description>"}`.
- **Security**: `cli_run_command` runs any public `Cli` method with the permissions of the server process. Treat it as an execute-class tool.

---

## Tool: `cli_list_commands`

### 1. Tool Purpose and Description

Introspects the `Cli` class and lists every public callable attribute with the first line of its docstring.

### 2. Invocation Name

`cli_list_commands`

### 3. Input Schema (Parameters)

None.

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `command_count` | `integer` | Number of commands listed | `26` |
| `commands` | `array[object]` | `{"name", "description"}` per command, sorted by name | `[{"name": "agent", "description": "Agent management subcommands"}]` |
| `message` | `string` | Error description (only on error) | `"..."` |

### 5. Error Handling

- Import or introspection failures return the error shape.

### 6. Idempotency

- **Idempotent**: Yes

### 7. Usage Examples

```json
{
  "tool_name": "cli_list_commands",
  "arguments": {}
}
```

---

## Tool: `cli_run_command`

### 1. Tool Purpose and Description

Instantiates `Cli`, looks up the method named `command` and calls it with keyword arguments decoded from the `args` JSON object.

### 2. Invocation Name

`cli_run_command`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `command` | `string` | Yes | Name of a `Cli` method, as listed by `cli_list_commands` | `"modules"` |
| `args` | `string` | No | JSON object of keyword arguments for the method (default `""`, no arguments) | `"{}"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `command` | `string` | The command that ran (only on success) | `"modules"` |
| `result` | `any` | The method's return value (only on success) | `null` |
| `message` | `string` | Error description (only on error) | `"Unknown CLI command: nope"` |

### 5. Error Handling

- **Unknown command**: `{"status": "error", "message": "Unknown CLI command: <command>"}`.
- **Bad arguments**: `args` that decode to anything other than a JSON object return `"args must be a JSON object (dict), not <type>"`; invalid JSON returns the decoder error.
- Exceptions raised by the command are returned as the error shape.

### 6. Idempotency

- **Idempotent**: Depends on the command invoked.

### 7. Usage Examples

```json
{
  "tool_name": "cli_run_command",
  "arguments": {
    "command": "modules",
    "args": "{}"
  }
}
```

### 8. Security Considerations

- **Permissions**: Commands run in the MCP server process with its permissions and environment.
- **Trust**: Calls can change files or state depending on the command; gate them behind explicit trust.

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
