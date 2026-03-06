# Agent Guidelines - Terminal Interface

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Rich terminal output, interactive shell REPL, command execution, and tab completion for the Codomyrmex CLI. Powers all PAI Algorithm phase headers, progress bars, and structured result display. No MCP tools — access exclusively via direct Python import. Use `TerminalFormatter` for all agent-facing output formatting to maintain consistent visual style across the CLI.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package-level exports |
| `shells/` | `InteractiveShell` REPL implementation |
| `commands/` | Command registration and dispatch |
| `rendering/` | Rich output formatting and styling |
| `completions/` | Tab completion provider |
| `utils/` | `CommandRunner`, `TerminalFormatter` helpers |

## Key Classes

- **`InteractiveShell`** (in `shells/`) — REPL-style interactive shell with command registration
- **`CommandRunner`** (in `utils/`) — Execute shell commands and capture stdout/stderr/exit_code
- **`TerminalFormatter`** (in `utils/`) — Rich colored output: success(), error(), table(), progress
- **`CompletionProvider`** (in `completions/`) — Tab completion for CLI commands

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

## Operating Contracts

**DO:**
- Import from subpackages: `from codomyrmex.terminal_interface.utils import TerminalFormatter`
- Use `TerminalFormatter.success/error/table()` for all user-visible output
- Handle `KeyboardInterrupt` (Ctrl+C) gracefully in `InteractiveShell` loops
- Stream long command output rather than buffering to avoid memory issues

**DO NOT:**
- Use `print()` directly in agent code — use `TerminalFormatter` for consistent styling
- Block the shell thread on long-running operations without progress feedback
- Expose raw terminal escape codes — use the formatter's named methods only

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Rich terminal output, formatting, progress bars, interactive prompts; full display control | TRUSTED |
| **Architect** | Read + Design | Interface design review, output format specification | OBSERVED |
| **QATester** | Validation | Terminal output correctness, formatting verification, accessibility compliance | OBSERVED |
| **Researcher** | Read-only | Display research results via `TerminalFormatter.table()` | SAFE |

### Engineer Agent
**Use Cases**: Rendering BUILD/EXECUTE progress output, displaying structured results, creating interactive CLI flows.

### Architect Agent
**Use Cases**: Designing terminal UX patterns, reviewing output format specifications.

### QATester Agent
**Use Cases**: Validating terminal output format, testing display correctness during VERIFY phase.

### Researcher Agent
**Use Cases**: Displaying research findings in formatted tables, showing progress during long research operations.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/terminal_interface.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/terminal_interface.cursorrules)
