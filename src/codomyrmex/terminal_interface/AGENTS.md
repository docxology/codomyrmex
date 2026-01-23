# Codomyrmex Agents — src/codomyrmex/terminal_interface

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Foundation Layer module providing rich terminal interface utilities including interactive prompts, progress bars, formatted output, and shell interactions for the Codomyrmex platform.

## Active Components

### Interactive Shell

- `interactive_shell.py` - Interactive shell implementation
  - Key Classes: `InteractiveShell`, `CommandHandler`
  - Key Functions: `start_shell()`, `execute_command()`

### Terminal Utilities

- `terminal_utils.py` - Terminal utility functions
  - Key Classes: `ProgressBar`, `Spinner`, `TableFormatter`
  - Key Functions: `confirm_action()`, `prompt_input()`, `print_formatted()`

## Key Classes and Functions

| Class/Function | Purpose |
| :--- | :--- |
| `InteractiveShell` | Interactive command shell |
| `CommandHandler` | Command parsing and execution |
| `ProgressBar` | Progress bar display |
| `Spinner` | Loading spinner |
| `TableFormatter` | Format tabular data |
| `confirm_action()` | Prompt for user confirmation |
| `prompt_input()` | Get user input with validation |
| `print_formatted()` | Rich formatted output |

## Operating Contracts

1. **Foundation Status**: No dependencies on other Codomyrmex modules
2. **TTY Detection**: Graceful fallback when not in terminal
3. **ANSI Support**: Detect and respect terminal capabilities
4. **Accessibility**: Support for screen readers and plain text output
5. **Cross-Platform**: Works on Windows, macOS, and Linux

## Usage Example

```python
from codomyrmex.terminal_interface import (
    ProgressBar,
    confirm_action,
    prompt_input,
    TableFormatter
)

# Confirmation prompt
if confirm_action("Proceed with deployment?"):
    # Progress bar
    with ProgressBar(total=100, description="Deploying") as pbar:
        for i in range(100):
            # work...
            pbar.update(1)

# Table output
table = TableFormatter(headers=["Module", "Status"])
table.add_row(["agents", "OK"])
table.add_row(["llm", "OK"])
table.print()
```

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules (Foundation Layer)

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| logging_monitoring | [../logging_monitoring/AGENTS.md](../logging_monitoring/AGENTS.md) | Logging infrastructure |
| environment_setup | [../environment_setup/AGENTS.md](../environment_setup/AGENTS.md) | Environment validation |
| model_context_protocol | [../model_context_protocol/AGENTS.md](../model_context_protocol/AGENTS.md) | MCP standards |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tools
- [SPEC.md](SPEC.md) - Functional specification
