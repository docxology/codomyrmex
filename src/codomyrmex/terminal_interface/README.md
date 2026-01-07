# terminal_interface

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Rich CLI capabilities including colored output, progress bars, interactive prompts, and a custom shell (`codomyrmex>`). Provides cross-platform terminal interface (macOS, Linux, Windows) with table generation, command execution, and beautiful presentation using the `rich` library for consistent terminal rendering.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `interactive_shell.py` – File
- `terminal_utils.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.terminal_interface import (
    InteractiveShell,
    TerminalFormatter,
    CommandRunner,
)

# Create interactive shell
shell = InteractiveShell()
shell.add_command("help", handler=lambda: print("Available commands..."))
shell.add_command("status", handler=lambda: print("System status: OK"))
shell.run()  # Starts interactive shell

# Use terminal formatter
formatter = TerminalFormatter()
formatter.print_table(
    data=[["Name", "Status"], ["Module1", "OK"], ["Module2", "OK"]],
    title="System Status"
)

# Run commands
runner = CommandRunner()
result = runner.execute("python --version")
print(f"Output: {result.output}")
```

