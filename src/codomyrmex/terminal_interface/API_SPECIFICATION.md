# terminal_interface - API Specification

## Introduction

This document provides the complete API specification for the `terminal_interface` module.

## Module Overview

The `terminal_interface` module provides a set of tools for building interactive command-line interfaces, including colored formatting, table generation, and a command execution shell.

## Public API

### Main Functions

#### `function_name()`

**Description**: Initializes a new terminal session with specified parameters.

**Parameters**:
- `param1` (type): Description
- `param2` (type, optional): Description

**Returns**: Return type and description

**Example**:
```python
from codomyrmex.terminal_interface import function_name

result = function_name(param1="value")
```

## Classes

### `ClassName`

**Description**: Interface for custom terminal command handlers.

**Methods**:
- `method1()`: Description
- `method2(param)`: Description

## Constants

- `CONSTANT_NAME`: Description

## Exceptions

- `ModuleException`: Description

## Related Documentation

- [Module README](./README.md)
- [Usage Examples](../README.md#usage-examples) (See README for examples)
- [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md) (if applicable)

---

## Classes

### InteractiveShell

**Description**: Provides an interactive terminal interface for exploring and interacting with Codomyrmex modules and workflows.

#### Methods

**`__init__(prompt: str = "codomyrmex> ", **kwargs)`**
- Initialize interactive shell with custom prompt and configuration.
- **Parameters**: `prompt`, shell configuration options.
- **Errors**: Raises `ShellError` for initialization failures.

**`start()`**
- Start the interactive shell session.
- **Errors**: Raises `ShellError` for shell execution failures.

**`execute_command(command: str) -> str`**
- Execute a single command in the shell.
- **Parameters**: `command`, command string to execute.
- **Return Value**: Command execution result.
- **Errors**: Raises `CommandError` for command execution failures.

**`add_command_handler(command: str, handler: Callable)`**
- Register a custom command handler.
- **Parameters**: `command`, command name; `handler`, function to handle the command.

**`get_command_history() -> List[str]`**
- Retrieve command execution history.
- **Return Value**: List of previously executed commands.

### TerminalFormatter

**Description**: Provides utilities for formatting terminal output with colors, styles, and structured layouts.

#### Methods

**`format_success(message: str) -> str`**
- Format a success message with green color and checkmark.
- **Parameters**: `message`, message to format.
- **Return Value**: Formatted success message.

**`format_error(message: str) -> str`**
- Format an error message with red color and cross mark.
- **Parameters**: `message`, message to format.
- **Return Value**: Formatted error message.

**`format_warning(message: str) -> str`**
- Format a warning message with yellow color and warning symbol.
- **Parameters**: `message`, message to format.
- **Return Value**: Formatted warning message.

**`create_table(headers: List[str], rows: List[List[str]]) -> str`**
- Create a formatted table for terminal output.
- **Parameters**: `headers`, column headers; `rows`, table data rows.
- **Return Value**: Formatted table string.

**`format_json(data: Dict) -> str`**
- Format JSON data with syntax highlighting for terminal display.
- **Parameters**: `data`, dictionary to format.
- **Return Value**: Syntax-highlighted JSON string.

### CommandRunner

**Description**: Executes system commands with proper error handling and output capture.

#### Methods

**`run_command(command: List[str], **kwargs) -> Dict`**
- Execute a system command and capture output.
- **Parameters**: `command`, command as list of arguments; `**kwargs`, execution options.
- **Return Value**: Dictionary with stdout, stderr, return code, and execution time.
- **Errors**: Raises `CommandError` for execution failures.

**`run_command_async(command: List[str], **kwargs) -> subprocess.Popen`**
- Execute a system command asynchronously.
- **Parameters**: `command`, command as list of arguments; `**kwargs`, execution options.
- **Return Value**: Process object for asynchronous command.

**`check_command_available(command: str) -> bool`**
- Check if a command is available in the system PATH.
- **Parameters**: `command`, command name to check.
- **Return Value**: True if command is available, False otherwise.

## Integration Examples

### Interactive Shell Usage
```python
from codomyrmex.terminal_interface import InteractiveShell

# Create and start interactive shell
shell = InteractiveShell(prompt="codomyrmex> ")
shell.add_command_handler("analyze", lambda: "Running code analysis...")
shell.start()
```

### Terminal Formatting
```python
from codomyrmex.terminal_interface import TerminalFormatter

formatter = TerminalFormatter()

# Format different message types
print(formatter.format_success("Module loaded successfully"))
print(formatter.format_error("Failed to connect to database"))
print(formatter.format_warning("High memory usage detected"))

# Create formatted table
headers = ["Module", "Status", "Version"]
rows = [
    ["ai_code_editing", "Active", "0.1.0"],
    ["static_analysis", "Active", "0.1.0"],
    ["data_visualization", "Active", "0.1.0"]
]
print(formatter.create_table(headers, rows))
```

### Command Execution
```python
from codomyrmex.terminal_interface import CommandRunner

runner = CommandRunner()

# Run a command and get results
result = runner.run_command(["python", "--version"])
if result["return_code"] == 0:
    print(f"Python version: {result['stdout'].strip()}")
else:
    print(f"Error: {result['stderr']}")

# Check if command is available
if runner.check_command_available("git"):
    print("Git is available")
else:
    print("Git is not installed")
```

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
