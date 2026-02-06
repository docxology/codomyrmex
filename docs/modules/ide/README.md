# IDE Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Programmatic integration with IDEs: Antigravity, Cursor, VS Code.

## Key Features

- **IDE Client** — Abstract IDE interface
- **Cursor** — Cursor AI editor integration
- **Commands** — Execute IDE commands
- **Files** — File operations

## Quick Start

```python
from codomyrmex.ide import CursorClient, IDECommand

client = CursorClient()
client.connect()

result = client.execute(IDECommand.OPEN_FILE, path="src/main.py")

files = client.list_open_files()
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/ide/](../../../src/codomyrmex/ide/)
- **Parent**: [Modules](../README.md)
