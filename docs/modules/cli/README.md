# CLI Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Command-line interface framework with argument parsing, subcommands, and rich output.

## Key Features

- **Subcommands** — Nested command groups
- **Options** — Flags and arguments
- **Rich Output** — Colors and formatting
- **Completion** — Tab completion support

## Quick Start

```python
from codomyrmex.cli import CLI, Command, Option

cli = CLI(name="myapp")

@cli.command()
@Option("--name", "-n")
def greet(name: str):
    \"\"\"Greet a user.\"\"\"
    print(f"Hello, {name}!")

cli.run()
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/cli/](../../../src/codomyrmex/cli/)
- **Parent**: [Modules](../README.md)
