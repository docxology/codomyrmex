# Personal AI Infrastructure — Terminal Interface Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Terminal Interface module provides PAI integration for command execution and terminal output.

## PAI Capabilities

### Command Execution

Run shell commands:

```python
from codomyrmex.terminal_interface import CommandRunner

runner = CommandRunner()
result = runner.run("ls -la")

print(result.stdout)
print(f"Exit code: {result.returncode}")
```

### Rich Output

Format terminal output:

```python
from codomyrmex.terminal_interface import TerminalFormatter

fmt = TerminalFormatter()
fmt.print_success("Build completed!")
fmt.print_table(data, headers=["File", "Status"])
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `CommandRunner` | Execute commands |
| `TerminalFormatter` | Format output |
| `Shell` | Interactive shell |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
