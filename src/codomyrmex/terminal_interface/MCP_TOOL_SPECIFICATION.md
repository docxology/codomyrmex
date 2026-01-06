# terminal_interface - MCP Tool Specification

## Overview

This document specifies the Model Context Protocol (MCP) tools provided by the `terminal_interface` module.

## Available Tools

### `tool_name`

**Description**: [Tool description]

**Parameters**:
```json
{
  "param1": {
    "type": "string",
    "description": "Parameter description",
    "required": true
  },
  "param2": {
    "type": "integer",
    "description": "Parameter description",
    "required": false,
    "default": 0
  }
}
```

**Returns**: Return value description

**Example**:
```json
{
  "tool": "tool_name",
  "parameters": {
    "param1": "value",
    "param2": 42
  }
}
```

## Tool Registration

Tools are automatically registered when the module is imported:

```python
from codomyrmex.terminal_interface import register_tools

register_tools()
```

## Related Documentation

- [Module README](./README.md)
- [API Specification](./API_SPECIFICATION.md)
- [Usage Examples](../README.md#usage-examples) (See README for examples)

---

## Tool: `run_terminal_command`

### 1. Tool Purpose and Description

Execute terminal commands and capture output for system administration and development tasks.

### 2. Invocation Name

`run_terminal_command`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `command` | `string` | Yes | Terminal command to execute | `"ls -la"` |
| `working_directory` | `string` | No | Directory to execute command in | `"/path/to/project"` |
| `timeout_seconds` | `integer` | No | Command execution timeout | `30` |
| `capture_output` | `boolean` | No | Whether to capture and return command output | `true` |

### 4. Output Schema (Return Value)

```json
{
  "command": "ls -la",
  "return_code": 0,
  "stdout": "total 48
drwxr-xr-x  12 user  staff   384 Jan 18 13:46 .
drwxr-xr-x   3 user  staff    96 Jan 18 13:46 ..
-rw-r--r--   1 user  staff  1073 Jan 18 13:46 README.md
",
  "stderr": "",
  "execution_time": 0.023,
  "working_directory": "/path/to/project"
}
```

## Tool: `format_terminal_output`

### 1. Tool Purpose and Description

Format and enhance terminal output with colors, tables, and structured display for better readability.

### 2. Invocation Name

`format_terminal_output`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `content` | `string` | Yes | Content to format | `"Error: Connection failed"` |
| `format_type` | `string` | No | Type of formatting (success, error, warning, info, table, json) | `"error"` |
| `table_headers` | `array[string]` | No | Headers for table formatting | `["Name", "Status", "Size"]` |
| `table_rows` | `array[array[string]]` | No | Data rows for table formatting | `[["file1.txt", "active", "1.2MB"]]` |

### 4. Output Schema (Return Value)

```json
{
  "formatted_content": "\u001b[31m❌ Error: Connection failed\u001b[0m",
  "format_type": "error",
  "original_content": "Error: Connection failed",
  "terminal_codes": ["31m", "0m"]
}
```

## Tool: `start_interactive_shell`

### 1. Tool Purpose and Description

Launch an interactive terminal shell session for complex multi-step operations and exploration.

### 2. Invocation Name

`start_interactive_shell`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `shell_type` | `string` | No | Type of shell to launch (bash, zsh, python, codomyrmex) | `"codomyrmex"` |
| `working_directory` | `string` | No | Initial working directory | `"/path/to/project"` |
| `prompt` | `string` | No | Custom shell prompt | `"codomyrmex> "` |
| `startup_commands` | `array[string]` | No | Commands to execute on shell startup | `["cd /project", "git status"]` |

### 4. Output Schema (Return Value)

```json
{
  "shell_id": "shell_12345",
  "shell_type": "codomyrmex",
  "status": "started",
  "working_directory": "/path/to/project",
  "startup_commands_executed": 2,
  "available_commands": ["analyze", "build", "deploy", "help"]
}
```

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
