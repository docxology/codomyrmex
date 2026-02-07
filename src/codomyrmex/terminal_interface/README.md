# Terminal Interface Module

**Version**: v0.1.0 | **Status**: Active

Interactive terminal shells, command runners, and rich rendering.


## Installation

```bash
pip install codomyrmex
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
