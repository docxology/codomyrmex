# Agent Guidelines - Terminal Interface

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Interactive shell, command execution, and terminal rendering.

## Key Classes

- **InteractiveShell** — Interactive command shell
- **CommandRunner** — Execute commands
- **TerminalFormatter** — Rich terminal output
- **CompletionProvider** — Tab completion

## Agent Instructions

1. **Use rich output** — Colors and formatting
2. **Stream long output** — Don't buffer everything
3. **Handle signals** — Ctrl+C gracefully
4. **Validate input** — Check before execute
5. **Log commands** — Track command history

## Common Patterns

```python
from codomyrmex.terminal_interface import (
    InteractiveShell, CommandRunner, TerminalFormatter
)

# Execute commands
runner = CommandRunner()
result = runner.run("ls -la")
print(result.stdout)

# Rich formatting
fmt = TerminalFormatter()
fmt.print_success("Operation completed!")
fmt.print_error("Something went wrong")
fmt.print_table(data, headers=["Name", "Value"])

# Interactive shell
shell = InteractiveShell()
shell.register_command("status", show_status)
shell.run()  # Start REPL
```

## Testing Patterns

```python
# Verify command execution
runner = CommandRunner()
result = runner.run("echo hello")
assert "hello" in result.stdout

# Verify formatter
fmt = TerminalFormatter()
output = fmt.format_success("Test")
assert "Test" in output
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
