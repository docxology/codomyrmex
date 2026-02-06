# Personal AI Infrastructure — CLI Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The CLI module provides PAI integration for building command-line interfaces.

## PAI Capabilities

### Command Definition

Define CLI commands:

```python
from codomyrmex.cli import CLI, Option

cli = CLI(name="myapp")

@cli.command()
@Option("--name", "-n", required=True)
def greet(name: str):
    \"\"\"Greet a user.\"\"\"
    print(f"Hello, {name}!")

cli.run()
```

### Rich Output

Formatted terminal output:

```python
from codomyrmex.cli import Console

console = Console()
console.print_success("Done!")
console.print_table(data)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `CLI` | Build CLI apps |
| `Console` | Rich output |
| `Option` | Parse arguments |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
