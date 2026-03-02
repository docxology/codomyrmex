# Terminal Interface Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

Interactive terminal shells, command runners, and rich rendering.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **ALL PHASES** | Rich terminal output for all Algorithm phase headers and progress | Direct Python import |
| **EXECUTE** | Progress bars and live output during long-running operations | Direct Python import |

All PAI Algorithm output is rendered through the terminal interface. Every phase header, tool call result, and summary uses this module's rich formatting. Engineer agents use it for progress display during EXECUTE; all agents use it for structured output.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Submodules
- **`commands/`** — Command registry submodule.
- **`completions/`** — Autocomplete submodule.
- **`rendering/`** — Output rendering submodule.
- **`shells/`** — Terminal shell management utilities.
- **`utils/`** — Terminal utilities submodule.

## Quick Start

```python
from codomyrmex.terminal_interface import shells, commands, rendering

# Interactive shell
from codomyrmex.terminal_interface.shells import InteractiveShell

shell = InteractiveShell()
shell.register_command("status", show_status)
shell.register_command("run", run_task)
shell.start()  # Enter REPL

# Command execution
from codomyrmex.terminal_interface.utils import CommandRunner

runner = CommandRunner()
result = runner.run("ls -la")
print(result.stdout, result.exit_code)

# Rich formatting
from codomyrmex.terminal_interface.utils import TerminalFormatter

fmt = TerminalFormatter()
print(fmt.success("Operation completed"))
print(fmt.error("Something went wrong"))
print(fmt.table(data, headers=["Name", "Value"]))
```

## Submodules

| Module | Description |
|--------|-------------|
| `shells` | Interactive shell implementations |
| `commands` | Command registration and execution |
| `rendering` | Output formatting and styling |
| `completions` | Tab completion support |
| `utils` | Terminal utilities and helpers |

## Exports

| Class | Description |
|-------|-------------|
| `InteractiveShell` | REPL-style interactive shell |
| `CommandRunner` | Execute shell commands with capture |
| `TerminalFormatter` | Colored output and tables |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k terminal_interface -v
```

## Documentation

- [Module Documentation](../../../docs/modules/terminal_interface/README.md)
- [Agent Guide](../../../docs/modules/terminal_interface/AGENTS.md)
- [Specification](../../../docs/modules/terminal_interface/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
