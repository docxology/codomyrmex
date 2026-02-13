# Personal AI Infrastructure — Terminal Interface Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Terminal Interface module provides interactive terminal interfaces and utilities for the codomyrmex ecosystem. It includes submodules for shell interaction, command processing, output rendering, and tab completions. This is a **Foundation Layer** module that provides the human-facing terminal experience.

## PAI Capabilities

### Interactive Shell

Launch an interactive shell for exploring the codomyrmex ecosystem:

```python
from codomyrmex.terminal_interface import InteractiveShell

shell = InteractiveShell()
# Provides command history, tab completion, and rich output
```

### Command Execution

Run shell commands programmatically with structured output:

```python
from codomyrmex.terminal_interface import CommandRunner

runner = CommandRunner()
result = runner.run("ls -la")
print(result.stdout)
print(f"Exit code: {result.returncode}")
```

### Rich Output Formatting

Format terminal output with colors, tables, and status indicators:

```python
from codomyrmex.terminal_interface import TerminalFormatter

fmt = TerminalFormatter()
fmt.print_success("Build completed!")
fmt.print_table(data, headers=["File", "Status"])
```

### CLI Commands

```bash
codomyrmex terminal_interface themes  # List available terminal themes (default, rich, minimal, json)
codomyrmex terminal_interface info    # Show terminal environment info (TERM, shell, columns, lines)
```

## Submodules

| Submodule | Purpose |
|-----------|---------|
| `shells` | Interactive shell implementations (`InteractiveShell`) |
| `commands` | Command processing and dispatch |
| `rendering` | Output rendering and formatting |
| `completions` | Tab completion providers |
| `utils` | Terminal utilities (`CommandRunner`, `TerminalFormatter`) |

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `InteractiveShell` | Class (optional) | Interactive terminal shell with history and completions |
| `CommandRunner` | Class (optional) | Execute shell commands with structured results |
| `TerminalFormatter` | Class (optional) | Rich text formatting for terminal output |
| `shells` | Submodule | Shell implementations |
| `commands` | Submodule | Command processing |
| `rendering` | Submodule | Output rendering |
| `completions` | Submodule | Tab completion |
| `cli_commands()` | Function | CLI command registration |

Note: `InteractiveShell`, `CommandRunner`, and `TerminalFormatter` are optional imports — they depend on additional packages and may not be available in minimal installations.

## PAI Algorithm Phase Mapping

| Phase | Terminal Interface Contribution |
|-------|---------------------------------|
| **OBSERVE** | Terminal info provides context about the execution environment |
| **EXECUTE** | `CommandRunner` executes shell commands for agent work; `InteractiveShell` enables interactive exploration |
| **VERIFY** | `TerminalFormatter` renders verification results in human-readable format |

## Architecture Role

**Foundation Layer** — One of the 4 foundation modules. Provides the terminal interaction layer that the CLI module and other user-facing components build upon.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
