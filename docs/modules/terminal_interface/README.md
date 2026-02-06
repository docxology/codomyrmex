# Terminal Interface Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Interactive shell, command execution, and terminal rendering utilities.

## Key Features

- **Shell** — Interactive REPL
- **Commands** — Execute system commands
- **Formatting** — Rich terminal output
- **Completion** — Tab completion

## Quick Start

```python
from codomyrmex.terminal_interface import CommandRunner, TerminalFormatter

runner = CommandRunner()
result = runner.run("ls -la")
print(result.stdout)

fmt = TerminalFormatter()
fmt.print_success("Done!")
fmt.print_table(data, headers=["Name", "Value"])
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/terminal_interface/](../../../src/codomyrmex/terminal_interface/)
- **Parent**: [Modules](../README.md)
